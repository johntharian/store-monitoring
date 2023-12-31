import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models import models


def migrate_timezone(db: Session):
    """
    Migrate timezone data from csv to database.

    Parameters
    ----------
    db : Session
        database session
    """
    timezone = pd.read_csv("utils/migration/data/bq_pro.csv")

    # Begin a transaction
    db.begin()

    try:
        # Convert the DataFrame to a list of dictionaries
        timezone_data = timezone.to_dict(orient="records")

        # Insert data in batches
        for batch in chunk_list(timezone_data, chunk_size=100):
            db.bulk_insert_mappings(models.Timezone, batch)

        db.commit()
        print("Data migration successful")

    except IntegrityError as e:

        db.rollback()
        print(f"Error: {str(e)}")

    except Exception as e:

        db.rollback()
        print(f"Error: {str(e)}")


def migrate_bH(db: Session):
    """
    Migrate business hour data from csv to database.

    Parameters
    ----------
    db : Session
        database session
    """
    businessHours = pd.read_csv("utils/migration/data/menu_processed.csv")

    # Begin a transaction
    db.begin()

    try:
        # Convert the DataFrame to a list of dictionaries
        businessHours_data = businessHours.to_dict(orient="records")

        # Insert data in batches
        for batch in chunk_list(businessHours_data, chunk_size=100):
            db.bulk_insert_mappings(models.BusinessHours, batch)

        db.commit()
        print("Data migration successful")

    except IntegrityError as e:

        db.rollback()
        print(f"Error: {str(e)}")

    except Exception as e:

        db.rollback()
        print(f"Error: {str(e)}")


def migrate_store(db: Session):
    """
    Migrate store data from csv to database.

    Parameters
    ----------
    db : Session
        database session
    """
    stores = pd.read_csv("utils/migration/data/storestatus.csv")

    # Begin a transaction
    db.begin()

    try:
        # Convert the DataFrame to a list of dictionaries
        store_data = stores.to_dict(orient="records")

        # Insert data in batches
        for batch in chunk_list(store_data, chunk_size=100):
            db.bulk_insert_mappings(models.Stores, batch)

        db.commit()
        print("Data migration successful")

    except IntegrityError as e:
        db.rollback()
        print(f"Error: {str(e)}")

    except Exception as e:
        db.rollback()
        print(f"Error: {str(e)}")


def chunk_list(lst, chunk_size):
    """
    Reduces data to chunks

    Parameters
    ----------
    lst : data
        data to be reduced
    chunk_size : int
        sizz of the chunk

    Returns
    -------
    list
        list containing chunks of data
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]
