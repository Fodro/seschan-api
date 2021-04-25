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
    print("Error while connecting to db!", error)
finally:
    if (sqlite_connection):
        sqlite_connection.close()
        print("SQLite connection closed")

class Database():
	GET_BOARDS_QUERY = "SELECT * FROM boards"
	indexes = {
		"id": 0,
		"board_name": 0,
		"full_name": 0,
		"created_at": 0,
		"created_by": 0,
	}
	cursor
	sqlite_connection

	def __init__(self, DATABASE_FILE) -> None:
		self.sqlite_connection = sqlite3.connect(DATABASE_FILE)
		self.cursor = self.sqlite_connection.cursor()
		
		self.cursor.execute("SELECT name FROM PRAGMA_TABLE_INFO(\"boards\");")
		record = self.cursor.fetchall()
		for number in range(len(record)):
			self.indexes[record[number][0]] = number

	def get_boards(self):
		response = {
			"boards": []
		}

		name_index = self.indexes["board_name"]

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

		name_index = self.indexes["board_name"]
		id_index = self.indexes["id"]
		full_name_index = self.indexes["full_name"]

		self.cursor.execute(self.GET_BOARDS_QUERY)
		record = self.cursor.fetchall()
		boards = list(map(lambda item: [item[id_index], item[name_index], item[full_name_index]], record))
		
		for item in boards:
			if item[1] == name:
				response["name"] = item[1]
				response["full_name"] = item[2]
				break
		
		if len(response["name"]) == 0:
			return "404"
		
		return response
	
