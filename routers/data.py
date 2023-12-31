from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schema import schemas

from utils.migration import crud, migrate


router = APIRouter()

# @DESC - migrates store data
# @ROUTE - POST /migrate/store
# @PARAMS - None
@router.post("/migrate/store")
async def migrate_stores(db: Session = Depends(get_db)):
    migrate.migrate_store(db)


# @DESC - get store data
# @ROUTE - GET /data/store
# @PARAMS - None
@router.get("/data/store", response_model=list[schemas.Stores])
async def get_stores(db: Session = Depends(get_db)):
    stores = crud.get_stores(db, limit=100)
    return stores


# @DESC - migrates businessHour data
# @ROUTE - POST /migrate/businessHour
# @PARAMS - None
@router.post("/migrate/businessHours")
async def migrate_businessHours(db: Session = Depends(get_db)):
    migrate.migrate_bH(db)


# @DESC - get businessHour data
# @ROUTE - GET /data/businessHours
# @PARAMS - None
@router.get("/data/businessHours", response_model=list[schemas.BusinessHours])
async def get_businessHours(db: Session = Depends(get_db)):
    businessHours = crud.get_business_hours(db)
    return businessHours


# @DESC - migrates timezone data
# @ROUTE - POST /migrate/timezone
# @PARAMS - None
@router.post("/migrate/timezone")
async def migrate_timezone(db: Session = Depends(get_db)):
    migrate.migrate_timezone(db)


# @DESC - get timezone data
# @ROUTE - GET /data/timezone
# @PARAMS - None
@router.get("/data/timezone", response_model=list[schemas.Timezone])
async def get_timezone(db: Session = Depends(get_db)):
    timezones = crud.get_timezone(db)
    return timezones


# @DESC - delete all data from the database
# @ROUTE - DELETE /data/all
# @PARAMS - None
@router.delete("/data/all")
async def delete_all(db: Session = Depends(get_db)):
    crud.delete_all(db)
