import os
from datetime import datetime, date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event, create_engine
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class Base(object):
	""" BaseModel for the Optimizer """

	foreign_keys = []
	fields_to_ignore = []

	id =  Column(Integer, primary_key=True)

	# activity dates
	created_at = Column(DateTime)
	updated_at = Column(DateTime)


	# @declared_attr
	# def __tablename__(cls):
	# 	return cls.__name__


	def get_values(self) -> dict:
		""" get the values in dictionary format """
		date_format = "%Y-%m-%d"
		datetime_format = "%Y-%m-%d %H:%M:%S"
		fields_to_ignore = ['_sa_instance_state', "created_at", "updated_at"]
		if self.fields_to_ignore:
			fields_to_ignore.extend(self.fields_to_ignore)

		values = {}
		fields = list(self.__dict__.keys())
		fields.extend(self.foreign_keys)
		fields = list(set(fields) - set(fields_to_ignore))

		for field in fields:
			value = getattr(self, field, None)

			if isinstance(value, datetime):
				value = value.strftime(datetime_format)
			elif isinstance(value, date):
				value = value.strftime(date_format)
			elif isinstance(value, list):
				value = [ v.get_values() for v in value if getattr(v, 'get_values', None) ]

			values.update({ field: value })

		return values


BaseModel = declarative_base(cls=Base)

# @event.listens_for(BaseModel, 'before_insert')
def before_insert(target, value, instance):
	""" before insert hooks for the models """

	instance.created_at = datetime.now()
	instance.updated_at = datetime.now()

	if getattr(instance, 'before_insert', None) and callable(instance.before_insert):
		instance.before_insert()


# @event.listens_for(BaseModel, 'before_update')
def before_update(target, value, instance):
	""" before insert hooks for the models """

	instance.updated_at = datetime.now()
	if getattr(instance, 'before_update', None) and callable(instance.before_update):
		instance.before_update()
