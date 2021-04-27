import json

class Config():
	board_name = "SESChan"
	username = "Anon"
	lang = "ru"
	description = "Anonymous imageboard"

	def __init__(self) -> None:
		try:
			config_file = open("config.json", 'r')
			options = json.load(config_file)
			self.board_name = options['board_name']
			self.username = options['username']
			self.lang = options['lang']
			self.description = options['description']
		except:
			print("Error while loading config.json: loaded default configurationd")

config = Config()
