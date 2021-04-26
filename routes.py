from aiohttp import web
import json
from db import Database

routes = web.RouteTableDef()
db = Database("seschan.db")

@routes.get("/get_boards")
async def get_boards_handler(request: web.BaseRequest):
	response = db.get_boards()
	return web.json_response(response)

@routes.get("/get_board/{board_name}")
async def get_board_handler(request: web.BaseRequest):
	amount = int(request.query.get("amount", 10))
	page = int(request.query.get("page", 0))
	board_name = request.match_info['board_name']

	if page == 0:
		begin = 0
		end = amount
	else:
		begin = page*amount
		end = (page+1)*amount

	response = db.get_board(board_name)

	if response == "404":
		raise web.HTTPNotFound()

	response["threads"] = response["threads"][begin:end]

	return web.json_response(response)

@routes.get("/get_thread/{board_name}/{id}")
async def get_thread_handler(request: web.BaseRequest):
	board_name = request.match_info['board_name']
	thread_id = request.match_info['id']
	response = db.get_thread(board_name, thread_id)

	if response == "404":
		raise web.HTTPNotFound()

	return web.json_response(response)
