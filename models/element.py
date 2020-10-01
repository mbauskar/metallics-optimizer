from sqlalchemy.orm import relationship
from sqlalchemy import event, Column, String
from models.base_model import BaseModel, before_insert, before_update

class Element(BaseModel):
	""" Element model class for the optimizer """

	__tablename__ = 'element'

	name = Column(String(5), nullable=False)
	commodities = relationship("Commodity", secondary="chemical_concentrations")


event.listen(Element, 'before_insert', before_insert)
event.listen(Element, 'before_update', before_update)