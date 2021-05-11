from sqlalchemy import Column, Integer, String,  DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.sql.sqltypes import Date
from tzlocal import get_localzone

engine = create_engine('sqlite:///admin.db', echo=True)
Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	id = Column(Integer, primary_key=True)
	login = Column(String, nullable=False)
	password = Column(String, nullable=False)
	permission = Column(String, nullable=False)

	def __repr__(self) -> str:
		return "{} {} {} {}".format(self.login, self.password, self.permission, self.id)

class Auth_session(Base):
	__tablename__ = 'auth_sessions'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer)
	session_id = Column(String)
	create_date = Column(DateTime)
	expire_date = Column(DateTime)
	last_access_date = Column(DateTime)

	def __repr__(self) -> str:
		return "{} {} {} {} {}".format(self.user_id, self.session_id, self.create_date, self.expire_date, self.last_access_date)


Base.metadata.create_all(engine)

Database_Session = sessionmaker()
Database_Session.configure(bind=engine)
admin_db = Database_Session()

