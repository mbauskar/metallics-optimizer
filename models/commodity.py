from sqlalchemy.orm import relationship
from models.base_model import BaseModel, before_insert, before_update
from sqlalchemy import event, Column, String, Float, Integer, ForeignKey, Table

from models import get_db
from models.base_model import BaseModel, before_insert, before_update

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class ChemicalConcentrations(BaseModel):
	""" ChemicalConcentrations model for commodity """

	__tablename__ = 'chemical_concentrations'

	percentage = Column(Float(precision=2), default=0.0)
	element_id = Column(Integer, ForeignKey('element.id'))
	commodity_id = Column(Integer, ForeignKey('commodity.id'))


class Commodity(BaseModel):
	""" Commodity model for the metallics optimizers """

	__tablename__ = 'commodity'
	foreign_keys = [ 'chemical_compositions' ]

	name = Column(String(50), nullable=False, unique=True)
	price = Column(Float(precision=2), default=0.0)
	inventory = Column(Float(precision=2), default=0.0)
	chemical_compositions = relationship("ChemicalConcentrations")


event.listen(Commodity, 'before_insert', before_insert)
event.listen(Commodity, 'before_update', before_update)
event.listen(ChemicalConcentrations, 'before_insert', before_insert)
event.listen(ChemicalConcentrations, 'before_update', before_update)