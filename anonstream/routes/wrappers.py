import time
from functools import wraps

from quart import current_app, request, abort, make_response
from werkzeug.security import check_password_hash

from anonstream.user import sunset, user_for_websocket
from anonstream.chat import broadcast
from anonstream.helpers.user import generate_user
from anonstream.utils.user import generate_token

CONFIG = current_app.config
MESSAGES = current_app.messages
USERS_BY_TOKEN = current_app.users_by_token
USERS = current_app.users

def check_auth(context):
    auth = context.authorization
    return (
        auth is not None
        and auth.type == "basic"
        and auth.username == CONFIG["AUTH_USERNAME"]
        and check_password_hash(CONFIG["AUTH_PWHASH"], auth.password)
    )

def auth_required(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if check_auth(request):
            return await f(*args, **kwargs)
        hint = 'The broadcaster should log in with the credentials printed ' \
               'in their terminal.'
        body = (
            f'<p>{hint}</p>'
            if request.authorization is None else
             '<p>Wrong username or password. Refresh the page to try again.</p>'
            f'<p>{hint}</p>'
        )
        return body, 401, {'WWW-Authenticate': 'Basic'}

    return wrapper

def with_user_from(context):
    def with_user_from_context(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            timestamp = int(time.time())

            # Check if broadcaster
            broadcaster = check_auth(context)
            if broadcaster:
                token = CONFIG['AUTH_TOKEN']
            else:
                token = context.args.get('token') or context.cookies.get('token') or generate_token()

            # Remove non-visible absent users
            sunsetted_token_hashes = sunset(
                messages=MESSAGES,
                users_by_token=USERS_BY_TOKEN,
            )
            if sunsetted_token_hashes:
                await broadcast(
                    users=USERS,
                    payload={
                        'type': 'rem-users',
                        'token_hashes': sunsetted_token_hashes,
                    },
                )

            # Update / create user
            user = USERS_BY_TOKEN.get(token)
            if user is not None:
                user['seen']['last'] = timestamp
            else:
                user = generate_user(
                    timestamp=timestamp,
                    token=token,
                    broadcaster=broadcaster,
                )
                USERS_BY_TOKEN[token] = user
                await broadcast(
                    USERS,
                    payload={
                        'type': 'add-user',
                        'token_hash': user['token_hash'],
                        'user': user_for_websocket(user),
                    },
                )

            # Set cookie
            response = await f(user, *args, **kwargs)
            if context.cookies.get('token') != token:
                response = await make_response(response)
                response.headers['Set-Cookie'] = f'token={token}; path=/'
            return response

        return wrapper

    return with_user_from_context