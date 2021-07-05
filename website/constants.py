import toml
import os
import secrets
from flask import current_app

ROOT = os.path.dirname(current_app.root_path)
SEGMENTS_DIR   = os.path.join(ROOT, 'stream')
SEGMENTS_M3U8  = os.path.join(SEGMENTS_DIR, 'stream.m3u8')
STREAM_TITLE   = os.path.join(ROOT, 'title.txt')
STREAM_START   = os.path.join(SEGMENTS_DIR, 'start.txt')
STREAM_PIDFILE = os.path.join(SEGMENTS_DIR, 'pid.txt')

DIR_STATIC = os.path.join(ROOT, 'website', 'static')
DIR_STATIC_EXTERNAL = os.path.join(DIR_STATIC, 'external')

BROADCASTER_TOKEN = secrets.token_hex(8)

CONFIG_FILE = os.path.join(ROOT, 'config.toml')
with open(CONFIG_FILE) as fp:
    CONFIG = toml.load(fp)

# these two are accessed through `CONFIG`; they're just here for completeness
#CAPTCHA_FONTS = CONFIG['captcha']['fonts']
#HLS_TIME = CONFIG['stream']['hls_time']    # seconds per segment

VIEW_COUNTING_PERIOD = 30   # count views from the last x seconds
CHAT_TIMEOUT = 5    # seconds between chat messages
FLOOD_PERIOD = 20   # seconds
FLOOD_THRESHOLD = 3 # messages in FLOOD_PERIOD seconds

HOST_DEFAULT_NICKNAME = 'Broadcaster'
ANON_DEFAULT_NICKNAME = 'Anonymous'

CHAT_MAX_STORAGE = 1024
CHAT_SCROLLBACK = 100
MESSAGE_MAX_LENGTH = 256

CAPTCHA_SECRET_KEY = os.urandom(12)
CAPTCHA_LIFETIME = 3600

VIEWER_ABSENT_THRESHOLD = 86400

BACKGROUND_COLOUR = b'\x22\x22\x22'
BROADCASTER_COLOUR = b'\xff\x82\x80'

SEGMENT_INIT = 'init.mp4'

VIDEOJS_ENABLED_BY_DEFAULT = False

# notes: messages that can appear in the comment box
N_NONE            =  0
N_TOKEN_EMPTY     =  1
N_MESSAGE_EMPTY   =  2
N_MESSAGE_LONG    =  3
N_BANNED          =  4
N_TOOFAST         =  5
N_FLOOD           =  6
N_CAPTCHA_MISSING =  7
N_CAPTCHA_WRONG   =  8
N_CAPTCHA_USED    =  9
N_CAPTCHA_EXPIRED = 10
N_CAPTCHA_RANDOM  = 11
N_CONFIRM         = 12
N_APPEAR_OK       = 13
N_APPEAR_FAIL     = 14

NOTES = {N_NONE:            '',
         N_TOKEN_EMPTY:     'illegal token',
         N_MESSAGE_EMPTY:   'no message',
         N_MESSAGE_LONG:    'message too long',
         N_BANNED:          'you cannot chat',
         N_TOOFAST:         'resend your message',
         N_FLOOD:           'solve this captcha',
         N_CAPTCHA_MISSING: 'please captcha',
         N_CAPTCHA_WRONG:   'you got the captcha wrong',
         N_CAPTCHA_USED:    'captcha was used already',
         N_CAPTCHA_EXPIRED: 'the captcha expired',
         N_CAPTCHA_RANDOM:  'a wild captcha appears',
         N_CONFIRM:         'confirm you want to send',
         N_APPEAR_OK:       'appearance got changed',
         N_APPEAR_FAIL:     'name/pw too long; no change'}
