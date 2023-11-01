from sqlalchemy import asc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import string
import random
import pytz
import concurrent.futures
from threading import Thread


from models.models import Stores, BusinessHours, Timezone, Reports
# from .report import get_uptime_downtime_last_hour, get_uptime_downtime_last_day, get_uptime_downtime
from .report_optimized import get_uptime_downtime





# def get_timezone(db: Session, store_id: int):
#     timezone = db.query(Timezone).filter(Timezone.store_id == store_id).first()
#     if not timezone:
#         timezone = "America/Chicago"
#     else:
#         timezone = timezone.timezone_str

#     return timezone


# def get_start_and_end_time(db: Session, timezone: str, store_id: int, day: int):
#     local_time = db.query(BusinessHours).filter_by(store_id=store_id, day=day).first()

#     if not local_time:
#         start_time_local = datetime.strptime("00:00:00", "%H:%M:%S").time()
#         end_time_local = datetime.strptime("23:59:59", "%H:%M:%S").time()
#     else:
#         start_time_local = local_time.start_time_local
#         end_time_local = local_time.end_time_local

    

#     # return convert_to_utc(timezone, start_time_local, end_time_local)
#     return start_time_local,end_time_local


# def convert_to_utc(timezone, start_time_local, end_time_local):

#     start_date=datetime.combine(datetime.now(),start_time_local)
#     end_date=datetime.combine(datetime.now(),end_time_local)

#     timezone = pytz.timezone(timezone)

#     start_date_local = timezone.localize(start_date)
#     end_date_local= timezone.localize(end_date)

#     # # Convert to UTC
#     start_date_utc = start_date_local.astimezone(pytz.utc)
#     end_date_utc = end_date_local.astimezone(pytz.utc)


#     return start_date_utc.time(), end_date_utc.time()

# def get_local(utc_datetime,timezone):
#   utc_timezone = pytz.utc
#   timezone = pytz.timezone(timezone)

#   t = utc_timezone.localize(utc_datetime).astimezone(timezone)
#   return t



# def get_curr_time(timezone):
#     utc_datetime = datetime(2023, 1, 25, 18, 13, 22, 479220, tzinfo=pytz.utc)
#     timezone = pytz.timezone(timezone)

#     t = utc_datetime.astimezone(timezone)
#     return t


# def generate_random_id():
#     r=random.randint(4,8)
#     return ''.join(secrets.choice(string.ascii_lowercase) for i in range(r))
    
def create_report(db : Session,report_id : str) :
    report_location = f"reports/{report_id}.csv"
    db_report = Reports(report_id=report_id,status="Running",report_location=report_location)

    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def trigger_report(db):
    report_ids = db.query(Reports.report_id).all()

    report_id= "report"+str(len(report_ids) + 1)
    # data_location="reports"
    report = create_report(db, report_id)
    daemon = Thread(target=generate_report, args=(db,report_id),daemon=True)
    daemon.start()
    return report_id


def generate_report(db:Session, report_id:str):
    # get_uptime_downtime_last_day(db,report_id)
    get_uptime_downtime(db, report_id)
    # get_uptime_downtime_last_hour(db,report_id)
    # update_report_status(db,report_id)

def get_report(db:Session, report_id:str):
    report=db.query(Reports).filter(Reports.report_id == report_id).first()
    if report.status != "Complete":
        return "Running"
    else:
        return report

def update_report_status(db:Session, report_id:str):
    report = db.query(Reports).filter(Reports.report_id == report_id).first()

    if report:
        report.status = "Complete"
        print("status updated")
        db.commit()

