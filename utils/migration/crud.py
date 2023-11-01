from sqlalchemy.orm import Session

from models import models


def get_stores(db: Session, limit: int = 100):
    """
    Get stores from database.

    Parameters
    ----------
    db : Session
        database session
    limit : int
        number of records to retrieve from database

    Returns
    -------
    list 
        list of store data
    """
    return db.query(models.Stores).limit(limit).all()


def get_business_hours(db: Session):
    """
    Get business hours from database.

    Parameters
    ----------
    db : Session
        database session
    
    Returns
    -------
    list 
        list of business hour data
    """
    return db.query(models.BusinessHours).limit(100).all()


def get_timezone(db: Session):
    """
    Get timezone data from database.

    Parameters
    ----------
    db : Session
        database session

    Returns
    -------
    list 
        list of timezone data
    """
    return db.query(models.Timezone).limit(100).all()


def delete_all(db: Session):
    """
    Delete data from all tables

    Parameters
    ----------
    db : Session
        database session
    """
    db.query(models.Stores).delete()
    db.query(models.BusinessHours).delete()
    db.query(models.Timezone).delete()
    db.commit()
