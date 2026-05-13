#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from tqdm import tqdm
import mariadb
from my_lib import *
from pprint import pprint
log = create_logger('{}/{}.log'.format(config.log_dir, os.path.basename(__file__)))

conn = mariadb.connect(** config.mariadb_connect)


def check_url(l_log, l_url):
    try:
        response = requests.head(
            l_url,
            timeout=10,
            allow_redirects=True,
            verify=True
        )
        status = response.status_code
        final_url = response.url
        # l_log.debug(f"Status: {status}, Final url: {final_url}")
        return status == 200
    except requests.exceptions.SSLError:
        l_log.error("SSL Error")
        return False
    except requests.exceptions.Timeout:
        l_log.error("Timeout Error")
        return False
    except requests.exceptions.RequestException as e:
        l_log.error(f"Exception: {e}")
        return False

# Manual list
# manual_list=['0cXKkrf38Po','OrREtYi6PRM','hWA2BE3xLtw','icLaVRKHe78','qYLmN3lp1fk','i5s0KHzYbAY']
# for i in manual_list:
#     status, files = find_dlp_files(i, log)
#     print(files)
#
#     with conn.cursor(dictionary=True) as cursor:
#         cursor.execute("UPDATE `videos` SET `main_filename`=? "
#                        "WHERE `id` = ? AND `place` = 'youtube'",
#                        (Path(files['.mp4']).name, i))
#         conn.commit()
#         log.debug('Changed {} rows'.format(cursor.rowcount))
        # exit(0)


# Get archive video list
with conn.cursor(dictionary=True) as cursor:
    cursor.execute("SELECT id,oyid, main_filename FROM `videos` WHERE `place` = 'old.openyogaclass.com' AND main_filename is NOT NULL ")
    videos = cursor.fetchall()

# Check links
for i,video in enumerate(tqdm(videos)):
#for i,video in enumerate(videos):
    vid = video['oyid']
    filenames=[txt2url(video['main_filename'])]
    # name=txt2url(video['main_filename'][:-4])
    # filenames.append(f'{name}.mp3')
    # filenames.append(f'{name}.txt')
    for filename in filenames:
        url = f'https://archive.org/download/{vid}/{filename}'
        if not check_url(log,url):
            log.error(f"URL Error: {url}")


    #
    # # Get archive video list
    # with conn.cursor(dictionary=True) as cursor:
    #     cursor.execute("SELECT id, main_filename FROM `videos` WHERE `place` = 'archive' AND main_filename is NOT NULL")
    #     videos = cursor.fetchall()

exit(0)

# # Set archive main_filename
# with conn.cursor(dictionary=True) as cursor:
#     cursor.execute("SELECT v1.id,v1.oyid,v1.main_filename FROM `videos` v1 "
#                    "LEFT JOIN videos v2 ON v1.oyid = v2.oyid WHERE v1.place='youtube' and v2.place='archive' "
#                    "AND v1.main_filename is not null AND v2.main_filename is null")
#     results = cursor.fetchall()
#
# # for i,r in enumerate(tqdm(results)):
# for i,r in enumerate(results):
#     log.info(r)
#     with conn.cursor(dictionary=True) as cursor:
#         cursor.execute("UPDATE `videos` SET main_filename=? WHERE oyid=? AND place='archive'",
#                        (r['main_filename'], r['oyid']))
#
#         # if not i%500:
#         #     log.info("COMMIT")
#         conn.commit()
#         if cursor.rowcount > 2:
#             log.error(f"Change {cursor.rowcount} rows")
#             exit(-1)
#         # else:
#         #     log.debug(f"Change {cursor.rowcount} rows")
#     # exit(0)

# From disk
# with conn.cursor(dictionary=True) as cursor:
#     cursor.execute("SELECT id,oyid FROM videos WHERE place='old.openyogaclass.com' AND main_filename is NULL")
#     results = cursor.fetchall()

# for i,r in enumerate(tqdm(results)):
# # for i,r in enumerate(results):
#     log.info(r)
#     # print(Path(r['id']).name)
#     with conn.cursor(dictionary=True) as cursor:
#         cursor.execute("UPDATE `videos` SET main_filename=? WHERE oyid=? AND place='old.openyogaclass.com'",
#                        (Path(r['id']).name, r['oyid']))
#
#         # if not i%50:
#         #     exit(0)
#         #     log.info("COMMIT")
#         conn.commit()
#         if cursor.rowcount !=1 :
#             log.error(f"Change {cursor.rowcount} rows")
#             exit(-1)
#         else:
#             log.debug(f"Change {cursor.rowcount} rows")
    # exit(0)
