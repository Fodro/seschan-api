import aiohttp_jinja2
import jinja2
import asyncio
from config import config

async def login_tmpl(request, context):
	context['board_name'] = config.board_name
	response = aiohttp_jinja2.render_template('login.jinja2', request, context)
	return response

async def after_login_tmpl(request, context):
	context['board_name'] = config.board_name
	response = aiohttp_jinja2.render_template('after_login.jinja2', request, context)
	return response

async def panel_tmpl(request):
	context = {
		"board_name": config.board_name,
	}
	respose = aiohttp_jinja2.render_template('panel.jinja2', request, context)
	return respose
