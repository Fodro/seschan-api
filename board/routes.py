from aiohttp import web
from board.db import db

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
		response = db.new_thread(data)
	except:
		raise web.HTTPBadRequest()


	if response == '404':
		raise web.HTTPNotFound()

	return web.json_response(response)

@routes.post("/{thread_id}/new_reply")
async def new_reply_handler(request: web.BaseRequest):
	try:
		body = await request.json()
		thread_id = request.match_info['thread_id']
		reply_data = {
			"author": body["author"],
			"body": body["body"],
			"media": body["media"],
			"reply_to": body["reply_to"],
		}
		response = db.new_reply(thread_id, reply_data)
	except:
		raise web.HTTPBadRequest()

	return web.json_response({"status":"ok"})
