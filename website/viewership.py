import math
import os
import threading
import time
import website.utils.colour as colour
import website.utils.tripcode as tripcode
from website.constants import ANON_DEFAULT_NICKNAME, BROADCASTER_COLOUR, BROADCASTER_TOKEN, HLS_TIME, HOST_DEFAULT_NICKNAME, SEGMENTS_DIR, VIEW_COUNTING_PERIOD

viewers = {}
segment_views = {}
lock = threading.Lock()

def default_nickname(token):
    if token == BROADCASTER_TOKEN:
        return HOST_DEFAULT_NICKNAME
    return ANON_DEFAULT_NICKNAME

def setdefault(token):
    if token in viewers:
        return
    viewers[token] = {'token': token,
                      'comment': float('-inf'),
                      'heartbeat': int(time.time()),
                      'verified': False,
                      'recent_comments': [],
                      'nickname': default_nickname(token),
                      'colour': colour.gen_colour(token.encode(), *(viewers[token]['colour'] for token in viewers)),
                      'banned': False,
                      'tripcode': tripcode.default(),
                      'broadcaster': False}
    if token == BROADCASTER_TOKEN:
        viewers[token]['broadcaster'] = True
        viewers[token]['colour'] = BROADCASTER_COLOUR
        viewers[token]['verified'] = True

def heartbeat(token):
    setdefault(token)
    viewers[token]['heartbeat'] = int(time.time())

def view_segment(n, token=None, check_exists=True):
    # n is None if segment_hook is called in ConcatenatedSegments and the current segment is init.mp4
    if n == None:
        return

    # technically this is a race condition
    if check_exists and not os.path.isfile(os.path.join(SEGMENTS_DIR, f'stream{n}.m4s')):
        return

    with lock:
        now = int(time.time())
        segment_views.setdefault(n, []).append({'time': now, 'token': token})
        print(f'seg{n}: {token}')

def count_site_tokens():
    '''
    Return the number of viewers who have sent a heartbeat or commented in the last 30 seconds
    '''
    n = 0
    now = int(time.time())
    for token in set(viewers):
        if max(viewers[token]['heartbeat'], viewers[token]['comment']) >= now - VIEW_COUNTING_PERIOD:
            n += 1
    return n

# TODO: account for the stream restarting; segments will be out of order
def count_segment_views(exclude_token_views=True):
    '''
    Estimate the number of viewers using only the number of views segments have had in the last 30 seconds
    If `exclude_token_views` is True then ignore views with associated tokens
    '''
    if not segment_views: # what?
        return 0

    # create the list of streaks; a streak is a sequence of consequtive segments with non-zero views
    streaks = []
    streak = []
    for i in range(min(segment_views), max(segment_views)):
        _views = segment_views.get(i, [])
        if exclude_token_views:
            _views = filter(lambda _view: _view['token'] == None, _views)
            _views = list(_views)
        if len(_views) == 0:
            if streak:
                streaks.append(streak)
            streak = []
        else:
            streak.append(len(_views))
    else:
        if streak:
            streaks.append(streak)

    total_viewers = 0
    for streak in streaks:
        n = 0
        _previous_n_views = 0
        for _n_views in streak:
            # any increase in views from one segment to the next means there must be new viewer
            n += max(_n_views - _previous_n_views, 0)
            _previous_n_views = _n_views
        total_viewers += n

    # this assumes every viewer views exactly VIEW_COUNTING_PERIOD / HLS_TIME segments
    average_viewers = sum(sum(streak) for streak in streaks) * HLS_TIME / VIEW_COUNTING_PERIOD

    print(f'count_segment_views: {total_viewers=}, {average_viewers=}')
    return max(total_viewers, math.ceil(average_viewers))

def count_segment_tokens():
    # remove old views
    now = int(time.time())
    for i in set(segment_views):
        for view in segment_views[i].copy():
            if view['time'] < now - VIEW_COUNTING_PERIOD:
                segment_views[i].remove(view)
        if len(segment_views[i]) == 0:
            segment_views.pop(i)

    tokens = set()
    for i in segment_views:
        for view in segment_views[i]:
            # count only token views; token=None means there was no token
            if view['token'] != None:
                tokens.add(view['token'])

    return len(tokens)

def count():
    with lock:
        a, b = count_segment_tokens(), count_segment_views(exclude_token_views=True)
        print(f'count_segment_tokens={a}; count_segment_views={b}')
        return a + b
