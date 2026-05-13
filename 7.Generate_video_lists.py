#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mariadb
import csv
from urllib.parse import quote
from jinja2 import Template
from weasyprint import HTML
import config
from my_lib import *

# Manual data
force_update_channels_info = False # Need YouTube video files
ignore_channels = ['UCtXOsquZY9z8eb7ob3PM5Sg']
include_only_channels = [] #'UCR0-7hO2RMofHzerE8GcnxQ']

tree={}
conn = mariadb.connect(** config.mariadb_connect)

log = create_logger('{}/{}.log'.format(config.log_dir, os.path.basename(__file__)))
logging.getLogger("ia").setLevel(logging.WARNING)

# Get extra oyid
with conn.cursor(dictionary=True) as cursor:
    cursor.execute("SELECT oyid,id FROM videos WHERE place = 'archive' AND id != oyid")
    extra = cursor.fetchall()

eid = {}
for e in extra:
    if e['oyid'] in extra:
        eid[e['oyid']].append(e['id'])
    else:
        eid[e['oyid']] = [e['id']]

# Get youtube channels
with conn.cursor(dictionary=True) as cursor:
    cursor.execute("SELECT c.id, c.title, c.url, p.channel_id FROM `playlists` p "
                   "LEFT JOIN channels c on p.channel_id = c.id "
                   "GROUP BY p.channel_id ORDER BY c.idx DESC")
    channels_by_playlists=cursor.fetchall()
# pprint(channels_by_playlists)

c=0
for channel in channels_by_playlists:
    c = c + 1
    # if c>1:
    #     continue
    if 'title' in channel and channel['title'] is not None and force_update_channels_info is False:
        if channel['id'] in ignore_channels or (include_only_channels and channel['id'] not in include_only_channels):
            continue
        tree[c] = {'id': channel['id'], 'title': channel['title'], 'url': channel['url'], 'playlists': {}}
        log.debug(f'Get existing info: { channel }')
        continue

    channel_id= channel['channel_id']
    # Update channels info if needed
    log.debug(f"Update info for: { channel_id }")

    # Get video id from the most common channel id
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT v.id FROM `playlists` p "
                       "LEFT JOIN playlists_members pm ON p.id = pm.playlist_id "
                       "LEFT JOIN videos v ON pm.video_id = v.id WHERE p.channel_id= ? "
                       "GROUP BY v.channel ORDER BY count(v.channel) DESC LIMIT 1 ",
                       (channel_id,))
        yid=cursor.fetchall()[0]['id']

    log.debug(f'Video id: {yid}')
    status,files =find_dlp_files(yid,log)
    if status != 0:
        log.error("Files not found")
        exit(-1)

    # Read json
    with open(files['.info.json']) as f:
        data = json.load(f)
        url = data['uploader_url']
        title = data['channel']
        if title == "null":
            title = data['uploader_id']
        log.info(f'Url: {url}')
        log.info(f'Title: {title}')

    tree[c] = {'id': channel_id, 'title': title, 'url': url, 'playlists': {}}

    # Get from db
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM `channels` WHERE `id` = ?", (channel_id,))
        old_channel = cursor.fetchone()

    if old_channel is None:
        log.warning('Channel not found in the database, add')
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("INSERT INTO `channels`(`id`, `title`, `url`) VALUES (?,?,?)",
                           (channel_id, title, url))
            conn.commit()
        continue

    # Check existing channel
    need_update=False

    if channel['title'] != title:
        need_update=True
        log.warning(f'Update title: "{channel["title"]}" > "{title}"')

    if channel['url'] != url:
        need_update = True
        log.warning(f'Update url: {channel["url"]} > {url}')

    if need_update:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("UPDATE channels SET title=?, url=? WHERE id=?",
                           (title, url, channel_id))
            conn.commit()
            log.debug('Changed {} rows'.format(cursor.rowcount))


# Playlists and videos
for t in tree:
    channel_id=tree[t]['id']

    # Get YouTube playlists
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT id, title FROM `playlists` WHERE channel_id = ? ORDER BY title", (channel_id,))
        playlists=cursor.fetchall()

    # Get playlists members
    for playlist in playlists:
        tree[t]['playlists'][playlist['id']] = {'title': playlist['title']}

        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT oy.serial, v.main_filename, pm.video_id, pm.position, v.oyid, v.title FROM `playlists_members` pm "
                           "LEFT JOIN videos v ON pm.video_id = v.id "
                           "LEFT JOIN oyids oy ON v.oyid = oy.oyid "
                           "WHERE pm.playlist_id=? AND v.place = 'youtube'", (playlist['id'],))
            members=cursor.fetchall()

        tree[t]['playlists'][playlist['id']]['members'] = {}
        for m in members:
            tree[t]['playlists'][playlist['id']]['members'][m['position']] = {'id': m['video_id'],
                                                                              'title': m['title'],
                                                                              'oyid': m['oyid'],
                                                                              'serial': m['serial'],
                                                                              'main_filename': m['main_filename']}
            if m['oyid'] in eid:
                tree[t]['playlists'][playlist['id']]['members'][m['position']]['related'] = eid[m['oyid']]
                # pprint(tree[t]['playlists'][playlist['id']]['members'][m['position']])

# Make html for each channel
html_template = Template(open('oy_youtube2local.j2').read())

log.info(f'Writing {config.log_dir}/youtube-videos.html')
html = html_template.render(TODAY=datetime.today().strftime('%Y-%m-%d %H:%M'), TREE=tree)
with open(f'{config.log_dir}/youtube-videos.html', 'w', newline='', encoding='utf-8') as html_file:
    html_file.write(html)

log.info(f'Writing {config.log_dir}/youtube-videos.pdf')
HTML(string=html).write_pdf(f'{config.log_dir}/youtube-videos.pdf')


# Make csv
log.info(f'Writing {config.log_dir}/youtube-videos.csv')
with open(f'{config.log_dir}/youtube-videos.csv', 'w', newline='', encoding='utf-8') as csv_file:

    # csv headers
    fieldnames = ['Serial', 'Youtube', 'Archive', 'Title', 'mp4', 'mp3', 'Torrent']
    writer = csv.DictWriter(csv_file,
                            fieldnames=fieldnames,
                            delimiter=';',
                            quotechar='"',
                            quoting=csv.QUOTE_NONNUMERIC,
                            extrasaction='ignore')
    writer.writeheader()

    for row in tree:
        # Channels
        writer.writerow({})
        writer.writerow ({'Youtube': tree[row]['url'], 'Title': tree[row]['title']})
        writer.writerow({})

        # Playlists
        for playlist in tree[row]['playlists']:

            writer.writerow({})

            # Without playlists
            if playlist.startswith('unrelated-'):
                writer.writerow(({'Title': tree[row]['playlists'][playlist]['title']}))
            else:
                writer.writerow(({'Youtube': f'https://www.youtube.com/playlist?list={playlist}',
                                  'Title': tree[row]['playlists'][playlist]['title']}))
            # Videos
            for member in dict(sorted(tree[row]['playlists'][playlist]['members'].items())):
                m = tree[row]['playlists'][playlist]['members'][member]

                mp4 = f"https://archive.org/download/{m['oyid']}/{txt2url(m['main_filename'])}"
                mp3 = f'{mp4[:-1]}3'
                torrent = f"https://archive.org/download/{ m['oyid'] }/{ m['oyid'] }_archive.torrent"
                ar = f"https://archive.org/details/{m['oyid']}"

                if m['oyid'] in eid:
                    for e in eid[m['oyid']]:
                        ar = f"{ar} https://archive.org/details/{e}"

                writer.writerow({'Serial': m['serial'], 'Youtube': f"https://youtu.be/{m['id']}", 'Archive': f"{ar}",
                                 'Title': m['title'], 'mp4': mp4, 'mp3': mp3, 'Torrent': torrent})
