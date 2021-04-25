from aiohttp import web
import json
from db import Database

routes = web.RouteTableDef()
db = Database("seschan.db")

@routes.get("/get_boards")
async def get_boards_handler(request):
	response = db.get_boards()
	return web.json_response(response)

@routes.get("/get_board/{board_name}")
async def get_board_handler(request):
	board_name = request.match_info['board_name']
	response = db.get_board(board_name)

	if response == "404":
		raise web.HTTPNotFound()

	return web.json_response(response)

@routes.get("/get_thread/{board_name}/{id}")
async def get_thread_handler(request):
	board_name = request.match_info['board_name']
	thread_id = request.match_info['id']
	response = db.get_thread(board_name, thread_id)

	if response == "404":
		raise web.HTTPNotFound()

	return web.json_response(response)
