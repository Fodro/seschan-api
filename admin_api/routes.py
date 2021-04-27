from aiohttp import web
from aiohttp_session import get_session
from admin_api.db import *
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
		response = await panel_tmpl(request)
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
			login_data[entry[0]] = entry[1]
		record  = list(str(admin_db.query(User).filter_by(login=login_data['username']).first()).split())
	except:
		response = await after_login_tmpl(request, failed_context)
		return response
	if login_data['username'] == record[0] and login_data['password'] == record[1]:
		new_id = await auth.create_session(record[3])
		session['SESSIONID'] = new_id

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
	
	response = await after_login_tmpl(request, context)
	return response
