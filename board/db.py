import sqlite3
from datetime import datetime
from tzlocal import get_localzone
import nanoid

try:
    sqlite_connection = sqlite3.connect('seschan.db')
    cursor = sqlite_connection.cursor()
    print("Connecting Database...")

    sqlite_select_query = "select sqlite_version();"
    cursor.execute(sqlite_select_query)
    record = cursor.fetchall()
    print("SQLite version: ", record[-1][-1])
    cursor.close()

except sqlite3.Error as error:
    print("Error while connecting to db: ", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("SQLite connection closed")

class Database():
	GET_BOARDS_QUERY = "SELECT * FROM boards"
	GET_THREADS_QUERY = "SELECT * FROM threads"
	GET_THREADS_BY_BOARD_QUERY = "SELECT * FROM threads WHERE board_id={}" 
	GET_REPLIES_BY_THREAD_QUERY = "SELECT * FROM replies WHERE thread_id={}"
	GET_REPLIES_BY_REPLY_QUERY = "SELECT * FROM replies WHERE reply_to={}"
	GET_MEDIA_BY_REPLY_QUERY = "SELECT * FROM media WHERE post_id={}"
	
	NEW_THREAD_MUTATION = "INSERT INTO threads (created, updated, board_id, op_id, pinned) VALUES ({},{},{},{},FALSE) RETURNING *;"
	NEW_REPLY_MUTATION = "INSERT INTO replies (posted, author, body, reply_to, thread_id) VALUES ({},\"{}\",\"{}\",{},{}) RETURNING *;"
	NEW_MEDIA_MUTATION = "INSERT INTO media (post_id, media_url, media_type) VALUES ({}, \"{}\", \"{}\") RETURNING *;"
	NEW_BOARD_MUTATION = "INSERT INTO boards (board_name, created_at, created_by, full_name) VALUES(\"{}\", \"{}\", \"{}\", \"{}\");"

	DELETE_BOARD_MUTATION = "DELETE FROM boards WHERE board_name=\"{}\""

	UPDATE_OP_ID = "UPDATE threads SET op_id={} WHERE id={} RETURNING *;"

	CREATE_THREADS_TABLE = '''CREATE TABLE IF NOT EXISTS threads(
            id INTEGER PRIMARY KEY,
            created DATETIME NOT NULL,
            updated DATETIME NOT NULL,
            board_id INTEGER NOT NULL,
            op_id INTEGER NOT NULL UNIQUE,
			pinned BOOLEAN
        );
	'''
	CREATE_BOARDS_TABLE = '''CREATE TABLE IF NOT EXISTS boards(
            id INTEGER PRIMARY KEY,
			board_name TEXT NOT NULL UNIQUE,
			full_name TEXT NOT NULL UNIQUE,
			created_by TEXT NOT NULL,
            created_at DATETIME NOT NULL
        );
	'''
	CREATE_REPLIES_TABLE = '''CREATE TABLE IF NOT EXISTS replies(
            id INTEGER PRIMARY KEY,
            posted DATETIME NOT NULL,
            author TEXT NOT NULL,
            body TEXT NOT NULL,
            reply_to INTEGER,
            thread_id INTEGER NOT NULL
        );'''
	CREATE_MEDIA_TABLE = '''CREATE TABLE IF NOT EXISTS media(
			id INTEGER PRIMARY KEY,
			post_id INTEGER NOT NULL,
			media_url TEXT NOT NULL UNIQUE,
			media_type TEXT NOT NULL
		);'''
	
	board_props_index = {
		"id": 0,
		"board_name": 0,
		"full_name": 0,
		"created_at": 0,
		"created_by": 0,
	}
	thread_props_index = {
		"id": 0,
		"created": 0,
		"updated": 0,
		"board_id": 0,
		"op_id": 0,
		"pinned": 0,
	}
	reply_props_index = {
		"id": 0,
		"posted": 0,
		"author": 0,
		"body": 0,
		"reply_to": 0,
		"thread_id": 0,
	}
	media_props_index = {
		"id": 0,
		"post_id": 0,
		"media_url": 0,
		"media_type": 0,
	}
	
	cursor
	sqlite_connection


	def __init__(self, DATABASE_FILE) -> None:
		self.sqlite_connection = sqlite3.connect(DATABASE_FILE)
		self.cursor = self.sqlite_connection.cursor()

		self.cursor.execute(self.CREATE_BOARDS_TABLE)
		self.cursor.execute(self.CREATE_THREADS_TABLE)
		self.cursor.execute(self.CREATE_REPLIES_TABLE)
		self.cursor.execute(self.CREATE_MEDIA_TABLE)
		
		self.cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(\"boards\");")
		record = self.cursor.fetchall()
		for number in range(len(record)):
			item = record[number][0]
			self.board_props_index[item] = number

		self.cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(\"threads\");")
		record = self.cursor.fetchall()
		for number in range(len(record)):
			item = record[number][0]
			self.thread_props_index[item] = number

		self.cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(\"replies\");")
		record = self.cursor.fetchall()
		for number in range(len(record)):
			item = record[number][0]
			self.reply_props_index[item] = number

		self.cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(\"media\");")
		record = self.cursor.fetchall()
		for number in range(len(record)):
			item = record[number][0]
			self.media_props_index[item] = number


	def stop(self):
		print("\nClosing DB...")
		self.sqlite_connection.close()
	
	
	def get_boards(self):
		response = {
			"boards": []
		}

		name_index = self.board_props_index["board_name"]

		self.cursor.execute(self.GET_BOARDS_QUERY)
		record = self.cursor.fetchall()
		response["boards"] = list(map(lambda item: item[name_index], record))
		return response

	def get_board(self, name):
		response = {
			"name": "",
			"full_name": "",
			"threads": [],
		}

		name_index = self.board_props_index["board_name"]
		id_index = self.board_props_index["id"]
		full_name_index = self.board_props_index["full_name"]

		self.cursor.execute(self.GET_BOARDS_QUERY)
		record = self.cursor.fetchall()
		boards = list(map(lambda item: [item[id_index], item[name_index], item[full_name_index]], record))
		
		board_id = 0

		for item in boards:
			if item[1] == name:
				response["name"] = item[1]
				response["full_name"] = item[2]
				board_id = item[0]
				break
		
		if len(response["name"]) == 0:
			return "404"

		response["threads"] = self.get_threads(board_id)
		
		return response
	
	def get_threads(self, board_id):
		response = []

		id_index = self.thread_props_index["id"]
		created_index = self.thread_props_index["created"]
		updated_index = self.thread_props_index["updated"]
		board_id_index = self.thread_props_index["board_id"]
		op_id_index = self.thread_props_index["op_id"]
		pinned_index = self.thread_props_index["pinned"]

		self.cursor.execute(self.GET_THREADS_BY_BOARD_QUERY.format(board_id))
		record = self.cursor.fetchall()
		for item in record:
			thread = {
				"id": item[id_index],
				"created": item[created_index],
				"updated": item[updated_index],
				"board_id": item[board_id_index],
				"op_id": item[op_id_index],
				"pinned": item[pinned_index],
			}
			response.append(thread)
		response.sort(key=lambda item: item["updated"])

		return response

	def get_thread(self, board_name, thread_id_str):
		thread_id = int(thread_id_str)
		response = None

		board_id = -1
		board_name_index = self.board_props_index["board_name"]
		board_id_index = self.board_props_index["id"]

		op_id = -1
		id_index = self.thread_props_index["id"]
		created_index = self.thread_props_index["created"]
		op_id_index = self.thread_props_index["op_id"]

		self.cursor.execute(self.GET_BOARDS_QUERY)
		record = self.cursor.fetchall()

		for item in record:
			if board_name == item[board_name_index]:
				board_id = item[board_id_index]
				break
		
		if board_id == -1:
			return "404"

		self.cursor.execute(self.GET_THREADS_BY_BOARD_QUERY.format(board_id))
		record = self.cursor.fetchall()

		for item in record:
			if thread_id == item[id_index]:
				op_id = item[op_id_index]
				response = {
					"id": item[id_index],
					"created": item[created_index],
					"op_post": None,
					"replies": [],
				}
				break
		
		if op_id == -1:
			return "404"
		
		response["replies"] = self.get_replies(thread_id)

		for number in range(len(response["replies"])):
			item = response["replies"][number]
			if item["id"] == op_id:
				response["op_post"] = response["replies"].pop(number)
				break
		
		if response["op_post"] == None:
			return "404"

		return response


	def get_replies(self, thread_id):
		response = []

		id_index = self.reply_props_index["id"]
		posted_index = self.reply_props_index["posted"]
		author_index = self.reply_props_index["author"]
		body_index = self.reply_props_index["body"]

		self.cursor.execute(self.GET_REPLIES_BY_THREAD_QUERY.format(thread_id))
		record = self.cursor.fetchall()
		for item in record:
			reply = {
				"id": item[id_index],
				"posted": item[posted_index],
				"author": item[author_index],
				"body": item[body_index],
				"replies": [],
				"media": self.get_media(item[id_index]),
			}

			self.cursor.execute(self.GET_REPLIES_BY_REPLY_QUERY.format(item[id_index]))
			reply_record = self.cursor.fetchall()
			reply["replies"] = list(map(lambda sub_reply: sub_reply[id_index], reply_record))

			response.append(reply)

		return response

	
	def get_media(self, reply_id):
		media_url_index = self.media_props_index["media_url"]
		media_type_index = self.media_props_index["media_type"]

		self.cursor.execute(self.GET_MEDIA_BY_REPLY_QUERY.format(reply_id))
		response = self.cursor.fetchall()
		filter = lambda item: {
			"url": item[media_url_index],
			"type": item[media_type_index],
		}
		response = list(map(filter, response))

		return response

	def new_thread(self, thread_data):
		board_id = None

		board_name_index = self.board_props_index["board_name"]
		board_id_index = self.board_props_index["id"]

		thread_id_index = self.thread_props_index["id"]
		self.cursor.execute(self.GET_BOARDS_QUERY)
		record = self.cursor.fetchall()
		for item in record:
			if item[board_name_index] == thread_data["board_name"]:
				board_id = item[board_id_index]
				break
		
		if board_id == None:
			return "404"

		creation_time = datetime.now(get_localzone())
		creation_time = "\"" + str(creation_time)[:-6] + "\""

		self.cursor.execute(self.NEW_THREAD_MUTATION.format(creation_time, creation_time, board_id, -1))
		thread_id = self.cursor.fetchall()[0][thread_id_index]
		

		op_id = self.new_reply(thread_id, thread_data["op"])

		
		self.cursor.execute(self.UPDATE_OP_ID.format(op_id, thread_id))
		
		record = self.cursor.fetchall()[0]

		self.sqlite_connection.commit()

		return self.get_thread(thread_data["board_name"], thread_id)

		
	def new_reply(self, thread_id, reply_data):
		id_index = self.reply_props_index["id"]

		posted_time = datetime.now(get_localzone())
		posted_time = "\"" + str(posted_time)[:-6] + "\""

		try: 
			reply_to = reply_data["reply_to"]
		except:
			reply_to = "NULL"

		self.cursor.execute(self.NEW_REPLY_MUTATION.format(posted_time, reply_data["author"], reply_data["body"], reply_to,  thread_id))
		post_id = self.cursor.fetchall()[0][id_index]
		self.new_media(post_id, reply_data["media"])

		self.sqlite_connection.commit()


		return post_id

	def new_media(self, post_id, media_list):
		from base64 import b64decode
		for item in media_list:
			if ".avi" in item["filename"] or ".mkv" in item["filename"] or ".webm" in item["filename"] or ".mp4" in item["filename"]:
				media_type = "video"
			else:
				media_type = "image"
			
			file_name = media_type + "_" + \
			    nanoid.generate(size=8) + "_" + item["filename"]
			file = open(file_name, 'wb')
			file.write(b64decode(item["data"]))
			file.close()

			media_url = "/" + file_name

			self.cursor.execute(self.NEW_MEDIA_MUTATION.format(post_id, media_url, media_type))
			record = self.cursor.fetchall()

			self.sqlite_connection.commit()

		return 0

	def new_board(self, board_data, username):
		creation_time = datetime.now(get_localzone())
		creation_time = str(creation_time)[:-6]

		self.cursor.execute(self.NEW_BOARD_MUTATION.format(board_data["board_name"], creation_time, username, board_data["full_name"]))
		self.sqlite_connection.commit()

		return 0

	def delete_board(self, board_name):
		self.cursor.execute(self.DELETE_BOARD_MUTATION.format(board_name))
		self.sqlite_connection.commit()

		return 0

db = Database("seschan.db")
