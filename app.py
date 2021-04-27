from aiohttp import web
from board.routes import routes
from board.db import db

app = web.Application()
app.add_routes(routes)
web.run_app(app)
db.stop()