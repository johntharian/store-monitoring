from sqlalchemy.orm import Session

from models import models


def get_stores(db: Session, limit: int = 100):
    return db.query(models.Stores).limit(limit).all()


def get_business_hours(db: Session):
    return db.query(models.BusinessHours).limit(100).all()


def get_timezone(db: Session):
    return db.query(models.Timezone).limit(100).all()


def delete_all(db: Session):
    db.query(models.Stores).delete()
    db.query(models.BusinessHours).delete()
    db.query(models.Timezone).delete()
    db.commit()
