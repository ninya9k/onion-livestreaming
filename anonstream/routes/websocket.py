# SPDX-FileCopyrightText: 2022 n9k <https://git.076.ne.jp/ninya9k>
# SPDX-License-Identifier: AGPL-3.0-or-later

import asyncio

from math import inf

from quart import current_app, websocket

from anonstream.user import see, reading
from anonstream.websocket import websocket_outbound, websocket_inbound
from anonstream.routes.wrappers import with_user_from

@current_app.websocket('/live')
@with_user_from(websocket)
async def live(timestamp, user):
    queue = asyncio.Queue()
    user['websockets'][queue] = -inf
    reading(user, timestamp=timestamp)

    producer = websocket_outbound(queue, user)
    consumer = websocket_inbound(queue, user)
    try:
        await asyncio.gather(producer, consumer)
    finally:
        see(user)
        user['websockets'].pop(queue)
