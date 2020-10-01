from fastapi import APIRouter
from fastapi.responses import JSONResponse

from models import get_db
from models.user import User

router = APIRouter()

@router.get("/")
async def get_users():
	""" get and return all the users """

	db = get_db()
	return JSONResponse([ user.get_values() for user in db.query(User).all()])
