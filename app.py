from aiohttp import web
from routes import routes

app = web.Application()
app.add_routes(routes)
web.run_app(app)