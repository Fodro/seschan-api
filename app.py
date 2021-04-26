from aiohttp import web
from routes import routes
from db import db

app = web.Application()
app.add_routes(routes)
web.run_app(app)
db.stop()