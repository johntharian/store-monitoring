from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schema import schemas
from utils.migration.crud import delete_all, get_business_hours,get_stores,get_timezone
from utils.migration.migrate import migrate_bH,migrate_store,migrate_timezone


router = APIRouter()


@router.post("/migrate/store")
async def migrate_stores(db: Session = Depends(get_db)):
    migrate_store(db)


@router.get("/data/store", response_model=list[schemas.Stores])
async def get_stores(db: Session = Depends(get_db)):
    stores = get_stores(db, limit=100)
    return stores


@router.post("/migrate/businessHours")
async def migrate_businessHours(db: Session = Depends(get_db)):
    migrate_bH(db)


@router.get("/data/businessHours", response_model=list[schemas.BusinessHours])
async def get_businessHours(db: Session = Depends(get_db)):
    businessHours = get_business_hours(db)
    return businessHours


@router.post("/migrate/timezone")
async def migrate_timezone(db: Session = Depends(get_db)):
    migrate_timezone(db)


@router.get("/data/timezone", response_model=list[schemas.Timezone])
async def get_timezone(db: Session = Depends(get_db)):
    timezones = get_timezone(db)
    return timezones


@router.delete("/data/all")
async def delete_all(db: Session = Depends(get_db)):
    delete_all(db)
