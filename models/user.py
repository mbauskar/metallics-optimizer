from pbkdf2 import crypt
from datetime import datetime
from sqlalchemy import event, Column, DateTime, String, Boolean
from models.base_model import BaseModel, before_insert, before_update

from models.session import secret_key

class User(BaseModel):
	""" User model class for the optimizer """

	__tablename__ = 'user'

	# Database columns for the User
	email = Column(String(100), unique=True)
	username = Column(String(30), unique=True, nullable=False)
	password = Column(String(120), nullable=False)
	fullname = Column(String(120), nullable=False)
	is_active = Column(Boolean, default=False)

	# activity dates
	date_joined = Column(DateTime)
	last_login = Column(DateTime)


	fields_to_ignore = [ "password" ]

	def before_insert(self):
		""" before insert hook for the user model """

		# create the password hash
		self.password = crypt(self.password)
		self.date_joined = datetime.now()


	def verify_password(self, password):
		""" check if password is corrent or not """
		return self.password == crypt(password, self.password)


event.listen(User, 'before_insert', before_insert)
event.listen(User, 'before_update', before_update)