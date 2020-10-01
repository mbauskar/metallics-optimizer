from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from fastapi import Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse

from models import get_db
from models.user import User
from models.session import Session, secret_key, new_session

def get_logged_in_user(sid: str) -> User:
	""" get the logged in user """
	db = get_db()
	session = db.query(Session).filter(Session.session_key == sid,
		Session.expire_date > datetime.now()).first()

	if not session:
		raise HTTPException(status_code=403, detail="session expired, please login again")

	session_details = session.get_session_data()
	if not session_details and not session_details.get('user_id'):
		raise HTTPException(status_code=403, detail="invalid session, please login again")

	user = user = db.query(User).filter(User.id == session_details.get('user_id')).first()
	return user


def is_logged_in(sid: Optional[str] = Cookie(None)) -> None:
	""" check if the request is authenticated or not """
	if not sid:
		raise HTTPException(status_code=403, detail="session expired, please login again")

	user = get_logged_in_user(sid)
	if not user:
		raise HTTPException(status_code=403, detail="session expired, please login again")


def authenticate(username: str, password: str) -> dict:
	""" check if the password is correct or not and return the session key"""

	db = get_db()
	user = db.query(User).filter(User.username == username, User.is_active == 1).first()
	if not user:
		raise HTTPException(status_code=403, detail="Invalid username")
	elif not user.verify_password(password):
		raise HTTPException(status_code=403, detail="Invalid username or password")

	user.last_login = datetime.now()
	db.commit()

	session = {
		"user_id": user.id,
		"fullname": user.fullname,
		"session_id": new_session(user_id=user.id, fullname=user.fullname)
	}

	return session


def logout(sid: str) -> HTMLResponse:
	""" logout user, delete the session """
	response = HTMLResponse(status_code=204)
	if not sid:
		return response

	db = get_db()
	db.query(Session).filter(Session.session_key == sid).delete()
	return response