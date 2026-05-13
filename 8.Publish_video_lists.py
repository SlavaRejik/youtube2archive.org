#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config
from my_lib import *

item_name = 'OpenYoga_lists'

files_to_upload = [f'{config.log_dir}/youtube-videos.html',
                   f'{config.log_dir}/youtube-videos.pdf',
                   f'{config.log_dir}/youtube-videos.csv'
                   ]

# Set md
md = {'collection': 'opensource_movies',
      'title': 'OpenYoga files list',
      'language': 'rus',
      'licenseurl': 'https://creativecommons.org/publicdomain/zero/1.0/',
      'subject': ['OpenYoga', 'Yoga'],
      'description': 'Список файлов OpenYoga',
      'mediatype': 'web'}

log = create_logger('{}/{}.log'.format(config.log_dir, os.path.basename(__file__)))
logging.getLogger("ia").setLevel(logging.WARNING)

# Check active tasks
if check_active_tasks(item_name, log, wait=False) != 0:
    log.info(f'Found active tasks, waiting')
    while True:
        sleep(60)
        if check_active_tasks(item_name, log, wait=False) == 0:
            break


# Read item
item = internetarchive.get_item(item_name)
if item.item_metadata == {} or 'metadata' not in item.item_metadata:
    log.info(f"No metadata, (re)upload {item_name}")
    upload_files_to_archive(item_name, files_to_upload, md, log)
    exit(0)




# Get archive files
ar_files = {}
for file in item.files:
    if file['source'] == 'original' and not file['name'].endswith(('_files.xml', '_meta.sqlite',
                                                                   '_meta.xml', '__ia_thumb.jpg')):
        ar_files[file['name']] = file['md5']

# Files on disk with md5
files_on_disk = {}
for f in files_to_upload:
    files_on_disk[os.path.basename(f)] = {'md5': md5_checksum(f), 'path': f}

# pprint(ar_files)
# pprint(files_on_disk)

# Compare files
ar_files_to_delete = []
files_to_upload = []
for file_name in files_on_disk:
    if file_name in ar_files:
        if ar_files[file_name] == files_on_disk[file_name]['md5']:
            log.debug('Identical files {}'.format(file_name))
            del ar_files[file_name]
            continue
        else:
            log.debug('File exist but md5 different {}'.format(file_name))
            files_to_upload.append(files_on_disk[file_name]['path'])
            del ar_files[file_name]
    else:
        files_to_upload.append(files_on_disk[file_name]['path'])


# Original and derivative files to delete
for n in ar_files.keys():
    ar_files_to_delete.append(n)
    for i in item.files:
        if 'original' in i and i['original'] == n:
            ar_files_to_delete.append(i['name'])

# Delete files
if len(ar_files_to_delete):
    log.info(f'Files to delete in {item_name}')
    log.debug(ar_files_to_delete)
    delete_files_from_archive(item_name, ar_files_to_delete, log)
    need_another_round = 1
    changed_on_archive = True

# Upload files
if len(files_to_upload):
    log.info('Files to (re)upload to {}'.format(files_to_upload))
    log.debug(files_to_upload)
    upload_files_to_archive(item_name, files_to_upload, md, log)
