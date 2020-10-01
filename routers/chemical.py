from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
# from fastapi import Cookie, Depends, 

from models import get_db
from models.element import Element
from models.commodity import Commodity, ChemicalConcentrations

router = APIRouter()

# Models

class _Element(BaseModel):
	""" Element Model """
	id: int
	name: str


class _ChemicalConcentrations(BaseModel):
	""" Commodity Model """
	commodity_id: int
	element_id: int
	percentage: float = 0.0


class _Commodity(BaseModel):
	""" Commodity Model """
	id: int
	name: str
	price: float
	inventory: float


@router.get("/")
async def home():
	return HTMLResponse(status_code=204)


@router.get("/elements")
async def get_elements(db: Session = Depends(get_db)):
	""" get all the available elements from the database """
	elements = db.query(Element).all()
	return JSONResponse([ element.get_values() for element in elements ])


@router.get("/commodities")
async def get_commodities(db: Session = Depends(get_db)):
	""" get all the available elements from the database """
	commodities = db.query(Commodity).all()
	return JSONResponse([ commodity.get_values() for commodity in commodities ])


@router.get("/commodity/{id}")
async def get_commodity(id: int, db: Session = Depends(get_db)):
	""" get all the available elements from the database """
	commodity = db.query(Commodity).filter(Commodity.id==id).first()
	return JSONResponse(commodity.get_values() if commodity else {})


@router.put("/commodity/{id}")
async def update_commodity(id: int, commodity: _Commodity, db: Session = Depends(get_db)):
	""" get all the available elements from the database """
	commodity = commodity.dict()
	if id != commodity.get('id'):
		raise HTTPException(status_code=500, detail="Invalid Commodity Id")

	commodity.pop('id')
	db_commodity = db.query(Commodity).filter(Commodity.id==id).first()
	for field, val in commodity.items():
		setattr(db_commodity, field, val)

	db.commit()
	print(db_commodity.name)
	return JSONResponse(db_commodity.get_values() if db_commodity else {})


@router.post("/chemical-concentrations")
async def add_chemical_concentration(chemical_concentration: _ChemicalConcentrations,
	db: Session = Depends(get_db)):
	""" get all the available elements from the database """

	allowed_percentage = 0
	chemical_concentration = chemical_concentration.dict()
	percentage = chemical_concentration.get('percentage')
	element_id = chemical_concentration.get('element_id')
	commodity_id = chemical_concentration.get('commodity_id')
	chemical_concentrations = list(db.query(ChemicalConcentrations).filter(
		ChemicalConcentrations.commodity_id == commodity_id))

	unknown_element = db.query(Element).filter(Element.name == 'Unknown').first()
	print(chemical_concentrations)
	if not chemical_concentrations:
		db.add_all([
			ChemicalConcentrations(commodity_id=commodity_id,
				percentage=100.0 - percentage, element_id=unknown_element.id),
			ChemicalConcentrations(commodity_id=commodity_id,
				percentage=percentage, element_id=element_id)
		])
		db.commit()
		return JSONResponse(chemical_concentration)

	element_ids = [ instance.element_id for instance in chemical_concentrations ]
	if element_id in element_ids:
		raise HTTPException(status_code=500, detail="Chemical Concentrations for same element id already available")

	for instance in chemical_concentrations:
		if instance.element_id == unknown_element.id:
			allowed_percentage = instance.percentage

	if allowed_percentage < percentage:
		raise HTTPException(status_code=500, detail="All Chemical Concentrations percentage total for the commodity should be 100")

	db.add(ChemicalConcentrations(commodity_id=commodity_id, percentage=percentage,
		element_id=element_id))

	db.query(ChemicalConcentrations).filter(
		ChemicalConcentrations.commodity_id == commodity_id,
		ChemicalConcentrations.element_id == unknown_element.id
	).update({"percentage": allowed_percentage - percentage})

	db.commit()
	return JSONResponse(chemical_concentration)


@router.delete("/chemical-concentrations")
async def delete_chemical_concentration(chemical_concentration: _ChemicalConcentrations,
	db: Session = Depends(get_db)):
	""" get all the available elements from the database """

	to_update = None
	percentage = 0.0
	chemical_concentration = chemical_concentration.dict()
	element_id = chemical_concentration.get('element_id')
	commodity_id = chemical_concentration.get('commodity_id')
	unknown_element = db.query(Element).filter(Element.name == 'Unknown').first()

	chemical_concentrations = db.query(ChemicalConcentrations).filter(
		ChemicalConcentrations.commodity_id == commodity_id
	)
	element_ids = [ instance.element_id for instance in chemical_concentrations ]
	print(element_id, element_ids, unknown_element.id)
	if element_id not in element_ids or element_id == unknown_element.id:
		raise HTTPException(status_code=500, detail="Invalid element id")

	for instance in chemical_concentrations:
		if instance.element_id not in [unknown_element.id, element_id]:
			percentage += instance.percentage or 0.0
	

	if unknown_element.id not in element_ids:
		db.add(ChemicalConcentrations(
			commodity_id=commodity_id,
			percentage=100.0-percentage,
			element_id=unknown_element.id
		))
	else:
		db.query(ChemicalConcentrations).filter(
			ChemicalConcentrations.commodity_id == commodity_id,
			ChemicalConcentrations.element_id == unknown_element.id
		).update({"percentage": 100 - percentage})

	db.query(ChemicalConcentrations).filter(
		ChemicalConcentrations.element_id == element_id,
		ChemicalConcentrations.commodity_id == commodity_id
	).delete()
	db.commit()
	return JSONResponse({ "message": "Chemical Concentrations deleted" })