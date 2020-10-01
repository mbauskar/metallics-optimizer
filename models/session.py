import jwt
import uuid
from models import get_db
from sqlalchemy import event
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
secret_key = "9c7fe1b608bdd2b6a8b393d321e8a747decb48e886ff8ee1eb0b59770867"

class Session(Base):
	""" User model class for the optimizer """

	__tablename__ = 'session'

	session_key = Column(String(40), unique=True, nullable=False, primary_key=True)
	session_data = Column(Text, nullable=False)
	expire_date = Column(DateTime, nullable=False)


	def __init__(self, **kwargs):
		""" initialize the session instance """
		self._session_data = {}
		if not self.session_key and not kwargs:
			raise Exception('Invalid Session')
		elif not self.session_key:
			self._session_data = kwargs


	def encode_session_data(self):
		""" encode the session details """
		if not self._session_data:
			raise Exception('Invalid Session details')

		self.session_data = jwt.encode(self._session_data, secret_key,
			algorithm='HS256')


	def get_session_data(self):
		""" decode the session details """
		if not self.session_data:
			return {}

		return jwt.decode(self.session_data, secret_key, algorithms=['HS256'])


def new_session(**kwargs) -> str:
	""" create a new session for the user """
	session = Session(**kwargs)
	db = get_db()
	db.add(session)
	db.commit()
	return session.session_key


@event.listens_for(Session, 'before_insert')
def before_insert(target, value, instance):
	""" before insert hook for the session, generate session_key, and set 
		expiry date """

	instance.session_key = str(uuid.uuid4())
	instance.expire_date = datetime.now() + timedelta(hours=8)
	instance.encode_session_data()

