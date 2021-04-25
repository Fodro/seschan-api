import sqlite3

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
	
	cursor
	sqlite_connection


	def __init__(self, DATABASE_FILE) -> None:
		self.sqlite_connection = sqlite3.connect(DATABASE_FILE)
		self.cursor = self.sqlite_connection.cursor()

		self.cursor.execute(self.CREATE_BOARDS_TABLE)
		self.cursor.execute(self.CREATE_THREADS_TABLE)
		
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
		return [{"id": 1}, {"id": 2}]
