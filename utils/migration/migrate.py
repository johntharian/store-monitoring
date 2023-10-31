from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import pandas as pd

from models import models
from schema import schemas


# def migrate_store(db : Session) :

#     stores = pd.read_csv('utils/migration/data/storestatus.csv')
#     for index,row in stores.iterrows():
#         print(row.to_dict())
#         db_store= models.Stores(**row.to_dict())
#         db.add(db_store)
#         db.commit()
#         db.refresh(db_store)

#         break
#     print("Done")

def migrate_timezone(db: Session):
    timezone = pd.read_csv('utils/migration/data/bq_pro.csv')

    # Begin a transaction
    db.begin()
    
    try:
        # Convert the DataFrame to a list of dictionaries
        timezone_data = timezone.to_dict(orient='records')

        # Insert data in batches
        for batch in chunk_list(timezone_data, chunk_size=100):  # Adjust batch_size as needed
            db.bulk_insert_mappings(models.Timezone, batch)
        
        # Commit the transaction
        db.commit()
        print("Data migration successful")
    
    except IntegrityError as e:
        # Handle any database integrity errors (e.g., duplicate keys)
        db.rollback()
        print(f"Error: {str(e)}")
    
    except Exception as e:
        # Handle other exceptions
        db.rollback()
        print(f"Error: {str(e)}")


def migrate_bH(db: Session):
    businessHours = pd.read_csv('utils/migration/data/menu_processed.csv')

    # Begin a transaction
    db.begin()
    
    try:
        # Convert the DataFrame to a list of dictionaries
        businessHours_data = businessHours.to_dict(orient='records')

        # Insert data in batches
        for batch in chunk_list(businessHours_data, chunk_size=100):  # Adjust batch_size as needed
            db.bulk_insert_mappings(models.BusinessHours, batch)
        
        # Commit the transaction
        db.commit()
        print("Data migration successful")
    
    except IntegrityError as e:
        # Handle any database integrity errors (e.g., duplicate keys)
        db.rollback()
        print(f"Error: {str(e)}")
    
    except Exception as e:
        # Handle other exceptions
        db.rollback()
        print(f"Error: {str(e)}")


def migrate_store(db: Session):
    stores = pd.read_csv('utils/migration/data/storestatus.csv')

    # Begin a transaction
    db.begin()
    
    try:
        # Convert the DataFrame to a list of dictionaries
        store_data = stores.to_dict(orient='records')

        # Insert data in batches
        for batch in chunk_list(store_data, chunk_size=100):  # Adjust batch_size as needed
            db.bulk_insert_mappings(models.Stores, batch)
        
        # Commit the transaction
        db.commit()
        print("Data migration successful")
    
    except IntegrityError as e:
        # Handle any database integrity errors (e.g., duplicate keys)
        db.rollback()
        print(f"Error: {str(e)}")
    
    except Exception as e:
        # Handle other exceptions
        db.rollback()
        print(f"Error: {str(e)}")

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
