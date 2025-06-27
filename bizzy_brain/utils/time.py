# bizzy-gemini-version-scaffold/bizzy_brain/utils/time.py

import datetime

def now_local():
    return datetime.datetime.now()

def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")
