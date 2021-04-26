from aiohttp import web
import json
from db import db

routes = web.RouteTableDef()

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

@routes.post("/{board_name}/new_thread")
async def new_thread_handler(request: web.BaseRequest):
	try:
		body = await request.json()
		body_op = body["op"]
		op ={
			"author": body_op["author"],
			"body": body_op["body"],
			"media": body_op["media"],
		}
		data ={
			"board_name": request.match_info['board_name'],
			"op": op,
		}	
	except:
		raise web.HTTPBadRequest()

	response = db.new_thread(data)

	if response == '404':
		raise web.HTTPNotFound()

	return web.json_response(response)
