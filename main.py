from typing import Optional
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from fastapi import Depends, FastAPI, Cookie, Header, HTTPException

from models import get_db
from routers import users, chemical
from core.setup import setup_database
from core.auth import is_logged_in, authenticate, logout as _logout


app = FastAPI()
app.include_router(
	users.router,
	prefix="/users",
	tags=["Users"],
	dependencies=[Depends(is_logged_in)],
	responses={404: {"description": "Not found"}},
)
app.include_router(
	chemical.router,
	prefix="/chemical",
	tags=["Chemicals"],
	dependencies=[Depends(is_logged_in)],
	responses={404: {"description": "Not found"}},
)

setup_database()

@app.get("/")
def root():
	return {"Hello": "World"}


@app.post("/login")
async def login(username: str, password: str):
	""" authenticate and login user """
	response = JSONResponse(status_code=500)
	try:
		session = authenticate(username, password)
		session_id = session.pop("session_id")
		response = JSONResponse(content=session)
		response.set_cookie(key="sid", value=session_id)
	except HTTPException as e:
		response = JSONResponse(status_code=e.status_code, content={ "message": e.detail })
		response.delete_cookie(key="sid")

	return response


@app.post("/logout")
async def logout(sid: Optional[str] = Cookie(None)):
	""" logout user from site """
	response = _logout(sid)
	response.delete_cookie(key="sid")
	return response