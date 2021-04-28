from aiohttp import web
from aiohttp_session import get_session
from admin_api.db import *
from board.db import db
from admin_api.html import *
import admin_api.auth as auth

routes = web.RouteTableDef()

@routes.get("/")
async def serve_panel(request):
	session = await get_session(request)
	if 'SESSIONID' in session:
		record = await auth.verify_session(session['SESSIONID'])
		if not record:
			response = await login_tmpl(request, {})
			return response
		
		username = session['USERNAME']
		record = list(str(admin_db.query(User).filter_by(
				login=username).first()).split())
		context = {
			"username": record[0],
			"status": record[2],
		}
		response = await panel_tmpl(request, context)
		return response
	
	response = await login_tmpl(request, {})
	return response


@routes.post("/login")
async def handle_login(request: web.BaseRequest):
	session = await get_session(request)

	failed_context = {
		'title' : 'Login failed',
		'header' : 'Login attempt failed',
		'button': 'Try again',
	}

	successful_context = {
		'title': 'Login successful',
		'header': 'You\'re logged in!',
		'button': 'Go to the panel',
	}

	try:
		body = await request.read()
		decoded_body = body.decode('utf-8').split("&")
		login_data = {}
		for item in decoded_body:
			entry = list(item.split("="))
			login_data[entry[0]] = entry[1].replace("+", " ")
		record  = list(str(admin_db.query(User).filter_by(login=login_data['username']).first()).split())
	except:
		response = await after_login_tmpl(request, failed_context)
		return response
	if login_data['username'] == record[0] and login_data['password'] == record[1]:
		new_id = await auth.create_session(record[3])
		session['SESSIONID'] = new_id
		session['USERNAME'] = login_data['username']

		response = await after_login_tmpl(request, successful_context)
		return response
	else:
		response = await after_login_tmpl(request, failed_context)
		return response
	
@routes.get("/logout")
async def handle_logout(request):
	session = await get_session(request)

	context = {
		"title": "Logged out",
		"header": "You successfully logged out",
		"button": "Go to login page",
	}

	if "SESSIONID" in session:
		record = await auth.verify_session(session["SESSIONID"])
		if not record:
			response = await after_login_tmpl(request, context)
			return response
		deletion_response  = await auth.delete_session(session["SESSIONID"])
		if not deletion_response:
			print("Couldn't find this session")
	session["SESSIONID"] = ""
	session["USERNAME"] = ""
	response = await after_login_tmpl(request, context)
	return response


@routes.post("/new_board")
async def handle_new_board(request):
	session = await get_session(request)

	failed_context = {
            'title': 'Action error',
            'header': 'Action failed',
            'button': 'Return',
	}

	successful_context = {
            'title': 'Creation successful',
            'header': 'Successful',
            'button': 'Return to panel',
	}

	if 'SESSIONID' in session:
		record = await auth.verify_session(session['SESSIONID'])
		is_admin = await auth.verify_admin_rights(session['USERNAME'])
		if not record or not is_admin:
			response = await after_login_tmpl(request, failed_context)
			return response
		try:
			body = await request.read()
			decoded_body = body.decode('utf-8').split("&")
			board_data = {}
			for item in decoded_body:
				entry = list(item.split("="))
				board_data[entry[0]] = entry[1].replace("+", " ")
			db.new_board(board_data, session['USERNAME'])
			response = await after_login_tmpl(request, successful_context)
			return response
		except:
			response = await after_login_tmpl(request, failed_context)
			return response
	
	response = await after_login_tmpl(request, failed_context)
	return response

@routes.post("/delete_board")
async def handle_delete_board(request):
	session = await get_session(request)

	failed_context = {
            'title': 'Action error',
            'header': 'Action failed',
            'button': 'Return',
	}

	successful_context = {
            'title': 'Deletion successful',
            'header': 'Successful',
            'button': 'Return to panel',
	}

	if 'SESSIONID' in session:
		record = await auth.verify_session(session['SESSIONID'])
		is_admin = await auth.verify_admin_rights(session['USERNAME'])
		if not record or not is_admin:
			response = await after_login_tmpl(request, failed_context)
			return response
		try:
			body = await request.read()
			decoded_body = body.decode('utf-8').split("&")
			board_data = {}
			for item in decoded_body:
				entry = list(item.split("="))
				board_data[entry[0]] = entry[1].replace("+", " ")
			if board_data["approval"] != "on":
				response = await after_login_tmpl(request, failed_context)
				return response
			db.delete_board(board_data["board_name"])
			response = await after_login_tmpl(request, successful_context)
			return response
		except:
			response = await after_login_tmpl(request, failed_context)
			return response

	response = await after_login_tmpl(request, failed_context)
	return response
