from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine
from auth import hash_password, verify_password

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


@app.post("/register")
def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    user = models.User(
        username=username,
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    db: Session = SessionLocal()

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if user and verify_password(password, user.password):
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user
            }
        )

    return {"message": "Invalid Email or Password"}