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





def get_timezone(db: Session, store_id: int):
    timezone = db.query(Timezone).filter(Timezone.store_id == store_id).first()
    if not timezone:
        timezone = "America/Chicago"
    else:
        timezone = timezone.timezone_str

    return timezone


def get_start_and_end_time(db: Session, timezone: str, store_id: int, day: int):
    local_time = db.query(BusinessHours).filter_by(store_id=store_id, day=day).first()

    if not local_time:
        start_time_local = datetime.strptime("00:00:00", "%H:%M:%S").time()
        end_time_local = datetime.strptime("23:59:59", "%H:%M:%S").time()
    else:
        start_time_local = local_time.start_time_local
        end_time_local = local_time.end_time_local

    

    # return convert_to_utc(timezone, start_time_local, end_time_local)
    return start_time_local,end_time_local


def convert_to_utc(timezone, start_time_local, end_time_local):

    start_date=datetime.combine(datetime.now(),start_time_local)
    end_date=datetime.combine(datetime.now(),end_time_local)

    timezone = pytz.timezone(timezone)

    start_date_local = timezone.localize(start_date)
    end_date_local= timezone.localize(end_date)

    # # Convert to UTC
    start_date_utc = start_date_local.astimezone(pytz.utc)
    end_date_utc = end_date_local.astimezone(pytz.utc)


    return start_date_utc.time(), end_date_utc.time()

def get_local(utc_datetime,timezone):
  utc_timezone = pytz.utc
  timezone = pytz.timezone(timezone)

  t = utc_timezone.localize(utc_datetime).astimezone(timezone)
  return t



def get_curr_time(timezone):
    utc_datetime = datetime(2023, 1, 25, 18, 13, 22, 479220, tzinfo=pytz.utc)
    timezone = pytz.timezone(timezone)

    t = utc_datetime.astimezone(timezone)
    return t


def generate_random_id():
    r=random.randint(4,8)
    return ''.join(secrets.choice(string.ascii_lowercase) for i in range(r))
    
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

def get_one_hour_data(db: Session):
    curr_time = datetime.strptime(
    "2023-01-25 18:13:22.47922 UTC", "%Y-%m-%d %H:%M:%S.%f %Z"
    )
    res=[]
    c=1
    time_one_hour_ago = curr_time - timedelta(hours=1)
    day = time_one_hour_ago.weekday()
    store_ids = db.query(Timezone.store_id).all()
    store_ids = [store_id for (store_id,) in store_ids]
    for store_id in store_ids:
        uptime_hour=0
        downtime_hour=0
        store_id=5415949628544298000
        print(store_id)

        timezone = get_timezone(db, store_id)

        start_time, end_time = get_start_and_end_time(
            db, timezone, store_id, day
        )

        time = time_one_hour_ago.time()

        store_data = (
            db.query(Stores)
            .filter(
                Stores.store_id == store_id, 
                Stores.timestamp_utc > time_one_hour_ago , 
                Stores.timestamp_utc < curr_time
            )
            .order_by(asc(Stores.timestamp_utc))
            .all()
        )
        
        # if store_data:

        # if store_data:
        
        prev_time=None
        prev_status=None
        end=0
        uptime=0
        downtime=0
        # print(time_one_hour_ago)
        # print(curr_time)
        # time_one_hour_ago = get_local(time_one_hour_ago, timezone)
        # curr_time = get_local(curr_time,timezone)
        curr_time = get_curr_time(timezone)
        time_one_hour_ago = curr_time - timedelta(hours=1)
        print(time_one_hour_ago)
        print(curr_time)

        for data in store_data:
            time = data.timestamp_utc

            # print(time)
            # print(type(time))
            time=get_local(time,timezone)

            print(time)
            if prev_time is not None:
                # print("hey3")
                if time.time() < end_time:
                    td=(time-prev_time).total_seconds()
                    print(prev_time.time(),"-",time.time())
                    print(td/60)
                    prev_time=time
                    if data.status == 'active':
                        uptime+=(td/60)
                        prev_status='active'
                    else:
                        downtime+=(td/60)
                        prev_status='inactive'
                else:
                    end=1
                    td=(curr_time-time).total_seconds()
                    print(td/60)
                    print(time.time(),"-",curr_time.time())
                    if prev_status=='active':
                        uptime+=(td/60)
                    else:
                        downtime+=(td/60)

            else:
                # print("here")
                # print(start_time)
                # print(end_time)
                # print(time.time())
                # print(time)
                if start_time <= time.time() <=end_time:
                    # print(time)
                    # print(time_one_hour_ago.hour)
                    # print(time_one_hour_ago)
                    td= (time - time_one_hour_ago).total_seconds()
                    
                    print(time_one_hour_ago.time(),"-",time.time())
                    print(td/60)
                    prev_time = time

                    if data.status == 'active':
                        uptime+=(td/60)
                        prev_status='active'
                    else:
                        downtime+=(td/60)
                        prev_status='inactive'
                else:
                    end=1

        if end == 0 :
            print(curr_time , curr_time.hour, curr_time.minute )
            print(time, time.hour, time.minute )
            td=(curr_time.hour*60 +curr_time.minute - time.hour*60 - time.minute) 
            # td = (curr_time - time).total_seconds()
            print(time,"-",curr_time.time())
            print(td)
            if prev_status=='active':
                uptime+=(td)
            else:
                downtime+=(td)

            # if start_time <= time.time() <= end_time:
            #     if data.status == 'active':
            #         uptime_hour+=60
            #     else:

            #         # time_one_hour_ago_seconds = time_one_hour_ago.hour * 3600 + time_one_hour_ago.minute * 60 + time_one_hour_ago.second
            #         # time_seconds = time.time().hour * 3600 + time.time().minute * 60 + time.time().second
            #         # time_diff=time_seconds-time_one_hour_ago_seconds
            #         time_diff_till_downtime = (time-time_one_hour_ago).total_seconds()
            #         # print(time_diff_till_downtime/60)
            #         uptime_hour+=time_diff_till_downtime/60

            #         time_diff_till_uptime=(curr_time - time).total_seconds()
            #         downtime_hour+=time_diff_till_uptime/60


        print(uptime,downtime)
        break
        res.append({"store_id": store_id, "uptime_last_hour":uptime,"downtime_last_hour":downtime})

        c+=1
        if c==100:
            break
         
    return res
