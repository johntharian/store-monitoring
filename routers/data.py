from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models import models
from schema import schemas
from utils.migration import crud, migrate
from database import SessionLocal, engine, get_db


router = APIRouter()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@router.post("/migrate/store")
async def migrate_stores(db: Session = Depends(get_db)):
    migrate.migrate_store(db)


@router.get("/data/store", response_model=list[schemas.Stores])
async def get_stores(db: Session = Depends(get_db)):
    stores = crud.get_stores(db, limit=100)
    return stores


@router.post("/migrate/businessHours")
async def migrate_businessHours(db: Session = Depends(get_db)):
    migrate.migrate_bH(db)


@router.get("/data/businessHours", response_model=list[schemas.BusinessHours])
async def get_businessHours(db: Session = Depends(get_db)):
    businessHours = crud.get_business_hours(db)
    return businessHours


@router.post("/migrate/timezone")
async def migrate_timezone(db: Session = Depends(get_db)):
    migrate.migrate_timezone(db)


@router.get("/data/timezone", response_model=list[schemas.Timezone])
async def get_timezone(db: Session = Depends(get_db)):
    timezones = crud.get_timezone(db)
    return timezones


# @router.post('/data/store')
# async def create_store(store :schemas.Stores , db:Session = Depends(get_db)):
#     db_store = crud.create_store(db=db,store=store)
#     return db_store


# @router.post('/data/businessHours')
# async def create_businessHours(businessHours :schemas.BusinessHours , db:Session = Depends(get_db)):
#     db_businessHours = crud.create_business_hours(db=db,businessHours=businessHours)
#     return db_businessHours


# @router.post('/data/timezone')
# async def create_timezone(timezone :schemas.Timezone , db:Session = Depends(get_db)):
#     db_timezone= crud.create_timezones(db=db,timezone=timezone)
#     return db_timezone


@router.delete("/data/all")
async def delete_all(db: Session = Depends(get_db)):
    crud.delete_all(db)
