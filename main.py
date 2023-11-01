from fastapi import FastAPI
from sqlalchemy.orm import Session

from routers import reports, data

# import models


# from utils import migration
from schema import schemas
from models import models
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


app.include_router(reports.router)
app.include_router(data.router)
