import toml
import os
import secrets
from flask import current_app

ROOT = os.path.dirname(current_app.root_path)
SEGMENTS_DIR   = os.path.join(ROOT, 'stream')
SEGMENTS_M3U8  = os.path.join(SEGMENTS_DIR, 'stream.m3u8')
STREAM_TITLE   = os.path.join(ROOT, 'title.txt')

DIR_STATIC = os.path.join(ROOT, 'website', 'static')
DIR_STATIC_EXTERNAL = os.path.join(DIR_STATIC, 'external')

BROADCASTER_TOKEN = secrets.token_hex(8)

CONFIG_FILE = os.path.join(ROOT, 'config.toml')
with open(CONFIG_FILE) as fp:
    CONFIG = toml.load(fp)

# TODO: always read hls_time from stream.m3u8

VIEW_COUNTING_PERIOD = 30   # count views from the last x seconds
CHAT_TIMEOUT = 3    # seconds between chat messages
FLOOD_PERIOD = 20   # seconds
FLOOD_THRESHOLD = 4 # messages in FLOOD_PERIOD seconds

CHAT_MAX_STORAGE = 8192
CHAT_SCROLLBACK = 100
MESSAGE_MAX_LENGTH = 320

CAPTCHA_SECRET_KEY = os.urandom(12)
CAPTCHA_LIFETIME = 3600

VIEWER_ABSENT_THRESHOLD = 86400

BACKGROUND_COLOUR = b'\x23\x23\x23' # the same as in platform.css
BROADCASTER_COLOUR = b'\xff\x82\x80'

SEGMENT_INIT = 'init.mp4'

VIDEOJS_ENABLED_BY_DEFAULT = False

# if stream.m3u8 is not modified for this duration, consider the stream offline
# even if #EXT-X-ENDLIST is not present in the file. if this happens something
# has gone wrong in FFmpeg so we should turn off the stream.
STALE_PLAYLIST_THRESHOLD = 30

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
N_WORDFILTER      = 13
N_WORDFILTER_BAN  = 14
N_APPEAR_OK       = 15
N_APPEAR_FAIL     = 16

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
         N_WORDFILTER:      'blocked by word filter',
         N_WORDFILTER_BAN:  'banned by word filter',
         N_APPEAR_OK:       'appearance got changed',
         N_APPEAR_FAIL:     'name/pw too long; no change'}
