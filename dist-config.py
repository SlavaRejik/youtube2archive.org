youtube_dir = '/disk-2025/youtube'
log_dir = '/disk-2025/logs'

mariadb_connect = {
    'user': 'oyvideo',
    'password': 'password',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'oyvideo'
}


# yt_dlp options: https://github.com/yt-dlp/yt-dlp#filesystem-options
#yt_dlp = 'yt-dlp --cookies ~/tmp/cookies.txt  --proxy="socks5://127.0.0.1:8888"'
#yt_dlp = 'yt-dlp --cookies-from-browser chrome+basictext --proxy="socks5://127.0.0.1:8888"'
yt_dlp = 'yt-dlp --cookies-from-browser firefox --proxy="socks5://127.0.0.1:8888"'



channel_id = 'UCR0-7hO2RMofHzerE8GcnxQ' # @OpenYoga108

storage = 'test-2026'

telegram_api_key = '123'
telegram_chat_id = '123'
