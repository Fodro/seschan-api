from datetime import datetime, timedelta
from admin_api.db import *
from datetime import datetime

async def verify_session(id):
	record = list(str(admin_db.query(Auth_session).filter_by(
		session_id=id).first()).split())
	if record[0] == 'None':
		return False
	point_index = record[5].find(".")
	expire_date_str = record[4] + " " + record[5][:point_index]
	expire_date = datetime.strptime(expire_date_str, '%Y-%m-%d %H:%M:%S')
	current_date = datetime.now()
	if expire_date <= current_date:
		deletion_response = await delete_session(id)
		if not deletion_response:
			print("Couldn't find this session")
		return False
	return True

async def create_session(user_id):
	new_id = nanoid.generate(size=32)

	create_date = datetime.now(get_localzone())
	expire_date = datetime.now(get_localzone()) + timedelta(days=7)

	created_session = Auth_session(
		user_id=user_id, session_id=new_id, create_date=create_date, expire_date=expire_date, last_access_date=create_date)
	admin_db.add(created_session)
	admin_db.commit()

	return new_id

async def delete_session(id):
	try:
		admin_db.query(Auth_session).filter_by(session_id=id).delete()
		admin_db.commit()
		return True
	except:
		return False
