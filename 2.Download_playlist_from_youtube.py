#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pprint import pprint

import mariadb
from my_lib import *

conn = mariadb.connect(** config.mariadb_connect)
cursor = conn.cursor(dictionary=True)

log = create_logger('{}/{}.log'.format(config.log_dir, os.path.basename(__file__)))

r = run_cmd(log,f'{config.yt_dlp} --flat-playlist -J https://www.youtube.com/channel/{config.channel_id}/playlists')

if r['code'] != 0:
    log.error('Can\'t get list of playlists')
    log.error('Return code: {}'.format(r['code']))
    log.error('Stdout: {}'.format(r['stdout']))
    log.error('Stderr: {}'.format(r['stderr']))


playlists = json.loads(r['stdout'])
log.debug('{} "{}"'.format(playlists['channel_id'], playlists['channel']))

# Clean playlists
cursor.execute('DELETE FROM `playlists` WHERE `channel_id` = ?',(playlists['channel_id'],))
conn.commit()

# Create playlist for video without playlists
unrelated_playlist_id = f"unrelated-{playlists['channel_id']}"
cursor.execute("INSERT INTO `playlists` (`id`, `place`, `channel_id`, `title`, `description`, `ctime`)"
               "VALUES (?, 'youtube', ?, ?, NULL, current_timestamp())",
               (unrelated_playlist_id, playlists['channel_id'],'Videos without playlist'))
conn.commit()

# Delete playlist members for video without playlists
cursor.execute('DELETE FROM `playlists_members` WHERE `playlist_id` = ?', (unrelated_playlist_id,))

# Recreate playlist
playlists_description = {}
playlists_videos = {}
for playlist in playlists['entries']:
    log.debug('Channel {} playlist {} "{}"'.format(playlists['channel_id'], playlist['id'],playlist['title']))

    r = run_cmd(log, '{} --flat-playlist -J {}'.format(config.yt_dlp, playlist['url']))
    if r['code'] != 0:
        log.error('Can\'t get playlist info')
        log.error('Return code: {}'.format(r['code']))
        log.error('Stdout: {}'.format(r['stdout']))
        log.error('Stderr: {}'.format(r['stderr']))

    cursor.execute("INSERT INTO `playlists` (`id`, `place`, `channel_id`, `title`, `description`, `ctime`)"
                   "VALUES (?, 'youtube', ?, ?, NULL, current_timestamp())", (playlist['id'], playlists['channel_id'],
                 playlist['title']))
    conn.commit()

    playlist_info = json.loads(r['stdout'])

    cursor.execute('DELETE FROM `playlists_members` WHERE `playlist_id` = ?', (playlist['id'],))
    position = 0
    for playlist_member in playlist_info['entries']:
        if 'channel_id' in playlist_member and playlist_member['channel_id'] is None:
            log.info('Skip video: {} {} in {}'.format(playlist_member['id'], playlist_member['title'],
                                                      playlist['title']))
            continue

        # Update playlist description
        if playlist['id'] not in playlists_description:
            log.debug('Update description for playlist {}: "{}"'.format(playlist_member['title'],
                                                                        playlist_info['description']))
            playlists_description[playlist['id']] = playlist_info['description']
            cursor.execute("UPDATE `playlists` SET `description`=? WHERE `id` =?",
                           (playlist_info['description'], playlist['id']))
            conn.commit()
        # Add playlist member
        cursor.execute("INSERT INTO `playlists_members` (`playlist_id`, `video_id`, `position`, `ctime`) "
                       "VALUES (?, ?, ?, current_timestamp())",
                       (playlist['id'], playlist_member['id'], position))
        position += 1
        print('{} "{}"'.format(playlist_member['id'], playlist_member['title']))
        playlists_videos[playlist_member['id']]=1
    conn.commit()

log.info(f'Found {len(playlists_videos)} videos in playlists')

position = 0
for target in ['videos', 'streams', 'shorts']:
        # Get all public videos
        r = run_cmd(log,f'{config.yt_dlp} --flat-playlist -J https://www.youtube.com/channel/{config.channel_id}/{target}')

        if r['code'] != 0:
            log.error('Can\'t get list of playlists')
            log.error('Return code: {}'.format(r['code']))
            log.error('Stdout: {}'.format(r['stdout']))
            log.error('Stderr: {}'.format(r['stderr']))

        all_videos = json.loads(r['stdout'])
        log.info(f"Found {len(all_videos['entries'])} public {target} on channel")

        for video in all_videos['entries']:
            if video['id'] in playlists_videos:
                log.debug(f"Already in playlist {video['id']} {video['title']}")
                continue

            # Add playlist member
            cursor.execute("INSERT INTO `playlists_members` (`playlist_id`, `video_id`, `position`, `ctime`) "
                           "VALUES (?, ?, ?, current_timestamp())",
                           (unrelated_playlist_id, video['id'], position))
            conn.commit()
            position += 1
log.info(f"Add {position+1} elements without playlists")

cursor.execute("SELECT p.title, m.playlist_id, COUNT(*) FROM playlists_members m LEFT JOIN playlists p "
               "ON p.id = m.playlist_id WHERE channel_id = ? GROUP by m.playlist_id",(config.channel_id,))
for l in cursor.fetchall():
    print('{} {} {}'.format(l['COUNT(*)'], l['title'], l['playlist_id']))




