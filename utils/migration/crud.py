from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

from models import models
from schema import schemas


def get_stores(db : Session, limit: int = 100) :
    return db.query(models.Stores).limit(limit).all()

# def create_store(db : Session, store : schemas.Stores) :
#     # db_store = models.Stores(store_id=8419537941919820732,status="active",timestamp_utc=datetime.strptime("2023-01-22 12:09:39.388884 UTC","%Y-%m-%d %H:%M:%S.%f %Z"))
#     print(store.dict())
#     db_store= models.Stores(**store.dict())
#     db.add(db_store)
#     db.commit()
#     db.refresh(db_store)
#     return db_store

def get_business_hours(db :Session):
    return db.query(models.BusinessHours).limit(100).all()


# def create_business_hours(db : Session, businessHours : schemas.BusinessHours) :
#     # db_store = models.Stores(store_id=8419537941919820732,status="active",timestamp_utc=datetime.strptime("2023-01-22 12:09:39.388884 UTC","%Y-%m-%d %H:%M:%S.%f %Z"))
#     print(businessHours.dict())
#     db_businessHours= models.BusinessHours(**businessHours.dict())
#     db.add(db_businessHours)
#     db.commit()
#     db.refresh(db_businessHours)
#     return db_businessHours

def get_timezone(db :Session):
    return db.query(models.Timezone).limit(100).all()


# def create_timezones(db : Session, timezone : schemas.Timezone) :
#     # db_store = models.Stores(store_id=8419537941919820732,status="active",timestamp_utc=datetime.strptime("2023-01-22 12:09:39.388884 UTC","%Y-%m-%d %H:%M:%S.%f %Z"))
#     print(timezone.dict())
#     db_timezone= models.Timezone(**timezone.dict())
#     db.add(db_timezone)
#     db.commit()
#     db.refresh(db_timezone)
#     return db_timezone

def delete_all(db:Session ):
    db.query(models.Stores).delete()
    db.query(models.BusinessHours).delete()
    db.query(models.Timezone).delete()
    db.commit()
