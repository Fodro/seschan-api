from aiohttp import web
import base64
from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from admin_api.routes import routes
import aiohttp_jinja2, jinja2
from secret import get_secret

fernet_key = get_secret()
admin = web.Application()
secret_key = base64.urlsafe_b64decode(fernet_key)
setup(admin, EncryptedCookieStorage(secret_key))
aiohttp_jinja2.setup(admin, loader=jinja2.FileSystemLoader('admin_api/html/'))
admin.add_routes(routes)
web.run_app(admin)
