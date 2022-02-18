import asyncio

from quart import current_app, websocket

from anonstream.websocket import websocket_outbound, websocket_inbound
from anonstream.routes.wrappers import with_user_from

@current_app.websocket('/live')
@with_user_from(websocket)
async def live(user):
    queue = asyncio.Queue()
    user['websockets'].add(queue)

    producer = websocket_outbound(queue)
    consumer = websocket_inbound(queue, user)
    try:
        await asyncio.gather(producer, consumer)
    finally:
        user['websockets'].remove(queue)