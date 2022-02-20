import time
from datetime import datetime

from quart import current_app, escape

from anonstream.helpers.chat import generate_nonce_hash, get_scrollback
from anonstream.utils.chat import message_for_websocket

CONFIG = current_app.config
MESSAGES_BY_ID = current_app.messages_by_id
MESSAGES = current_app.messages
USERS_BY_TOKEN = current_app.users_by_token
USERS = current_app.users

class Rejected(ValueError):
    pass

def broadcast(users, payload):
    for user in users:
        for queue in user['websockets']:
            queue.put_nowait(payload)

def messages_for_websocket():
    return list(map(
        lambda message: message_for_websocket(
            user=USERS_BY_TOKEN[message['token']],
            message=message,
        ),
        get_scrollback(MESSAGES),
    ))

def add_chat_message(user, nonce, comment, ignore_empty=False):
    # special case: if the comment is empty, do nothing and return
    if ignore_empty and len(comment) == 0:
        return

    # check message
    message_id = generate_nonce_hash(nonce)
    if message_id in MESSAGES_BY_ID:
        raise Rejected('Discarded suspected duplicate message')
    if len(comment) == 0:
        raise Rejected('Message was empty')
    if len(comment) > 512:
        raise Rejected('Message exceeded 512 chars')

    # add message
    timestamp_ms = time.time_ns() // 1_000_000
    timestamp = timestamp_ms // 1000
    try:
        last_message = next(reversed(MESSAGES))
    except StopIteration:
        seq = timestamp_ms
    else:
        if timestamp_ms > last_message['seq']:
            seq = timestamp_ms
        else:
            seq = last_message['seq'] + 1
    dt = datetime.utcfromtimestamp(timestamp)
    markup = escape(comment)
    MESSAGES_BY_ID[message_id] = {
        'id': message_id,
        'seq': seq,
        'token': user['token'],
        'timestamp': timestamp,
        'date': dt.strftime('%Y-%m-%d'),
        'time_minutes': dt.strftime('%H:%M'),
        'time_seconds': dt.strftime('%H:%M:%S'),
        'nomarkup': comment,
        'markup': markup,
    }

    while len(MESSAGES_BY_ID) > CONFIG['MAX_CHAT_MESSAGES']:
        MESSAGES_BY_ID.pop(last=False)

    # broadcast message to websockets
    broadcast(
        USERS,
        payload={
            'type': 'chat',
            'seq': seq,
            'token_hash': user['token_hash'],
            'markup': markup,
        },
    )

    return markup
