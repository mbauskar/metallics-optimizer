import os
import json
import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import MetaData
from sqlalchemy import event, create_engine
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from models.user import User
from models.element import Element
from models.session import Session
from models.commodity import Commodity, ChemicalConcentrations

cur_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "optimizer.sqlite3")

SQLALCHEMY_DATABASE_URL = "sqlite:///{0}".format(db_path)

engine = create_engine(
	SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

DataBaseSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database() -> None:
	db = DataBaseSession()
	models = [ User, Session, Element, Commodity, ChemicalConcentrations ]
	for model in models:
		model_name = model.__tablename__
		if engine.dialect.has_table(engine, model.__tablename__):
			continue

		print("Creating {0} Table".format(model.__tablename__))
		model.__table__.create(bind=engine)

		fixtures_path = os.path.join(base_dir, "fixtures", "{}.json".format(model_name.lower()))
		has_fixture = os.path.isfile(fixtures_path)

		print("Has Fixtures {0}".format(has_fixture))
		if not has_fixture:
			continue

		fixtures = []
		with open(fixtures_path, "r") as _file:
			fixtures = json.loads(_file.read())

		print("Adding fixtures for {0}".format(model_name))
		[db.add(model(**fixture)) for fixture in fixtures]
	db.commit()