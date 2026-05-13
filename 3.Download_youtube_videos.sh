#!/bin/bash


./3.Download_youtube_videos.py

./_send_to_telegram.py $? 3.Download_youtube_videos.py.log

