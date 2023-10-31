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
import pandas as pd

def get_timezone(db:Session,store_id:str):
    timezone = db.query(Timezone).filter(Timezone.store_id==store_id).first()
    if not timezone:
        timezone = "America/Chicago"
    else:
        timezone=timezone.timezone_str
    return timezone

def get_local(utc_datetime:datetime,timezone:str):
  utc_timezone = pytz.utc
  timezone = pytz.timezone(timezone)
  t = utc_timezone.localize(utc_datetime).astimezone(timezone)
  return t

def get_start_end_time(db:Session,store_id:str,day:int):
    time = db.query(BusinessHours).filter(
        BusinessHours.store_id == store_id,
        BusinessHours.day ==day
    ).first()

    start_time = time.start_time_local
    end_time = time.end_time_local

    return start_time, end_time

def update_report_status(db:Session, report_id:str):
    report = db.query(Reports).filter(Reports.report_id == report_id).first()

    if report:
        report.status = "Complete"
        db.commit()

def one_hour_ago(db:Session,store_id:str, timezone:str, time_one_hour_ago:datetime, curr_time:datetime):
    uptime=0
    downtime=0
    prev_time=None
    prev_status=None

    end= 0
    store_data = db.query(Stores).filter(
            Stores.store_id == store_id,
            Stores.timestamp_utc > time_one_hour_ago,
            Stores.timestamp_utc < curr_time
        ).order_by(asc(Stores.timestamp_utc)).all()

    curr_time_local = get_local(curr_time,timezone)
    time_one_hour_ago_local = curr_time_local - timedelta(hours=1)

    day=curr_time_local.weekday()
    start_time, end_time = get_start_end_time(db,store_id,day)

    if len(store_data) > 0:
        
        for store in store_data :
            poll = store.timestamp_utc
            poll_local = get_local(poll, timezone)

            if prev_time is not None:
                if poll_local.time() < end_time:
                    # print(poll_local.time(),"here")
                    td=((poll_local - prev_time).total_seconds())/60
                    
                    prev_time=poll_local

                    if store.status == 'active':
                        uptime+=td
                    else:
                        downtime+=td
                    prev_status = store.status

                else:
                    end = 1
                    td = ((curr_time_local - prev_time).total_seconds())/60
                    
                    if prev_status =='active':
                        uptime+=td
                    else:
                        downtime+=td

            else:
                if start_time <= poll_local.time() <= end_time:
                    td = ((poll_local - time_one_hour_ago_local).total_seconds())/60
                    
                    prev_time = poll_local

                    if store.status == 'active' :
                        uptime+=td
                        # prev status
                    else:
                        downtime+=td
                        # prev staus

                    prev_status = store.status
                else:
                    end=1
                
        if end == 0:
            td=((curr_time_local - prev_time).total_seconds())/60
            
            if prev_status =='active':
                uptime+=td
            else:
                downtime+=td

    return uptime,downtime

def one_day_ago(db:Session,store_id:str, timezone:str, time_one_day_ago:datetime, curr_time:datetime):
    uptime=0
    downtime=0
    prev_time = None
    prev_status = None
    
    timezone = get_timezone(db,store_id)
    
    curr_time_local = get_local(curr_time,timezone)
    time_one_day_ago_local = curr_time_local - timedelta(days=1)
    
    store_data = db.query(Stores).filter(
        Stores.store_id == store_id,
        Stores.timestamp_utc > time_one_day_ago,
        Stores.timestamp_utc < curr_time
    ).order_by(asc(Stores.timestamp_utc)).all()

    if len(store_data) > 0:
        
        for store in store_data :
            poll = store.timestamp_utc
            poll_local = get_local(poll, timezone)

            poll_day = poll_local.weekday()
            
            start_time, end_time = get_start_end_time(db,store_id,poll_day)
            
            if start_time <= poll_local.time() <=end_time:
                if prev_time is not None:
                    if prev_time.time() > start_time:
                        td=((poll_local - prev_time).total_seconds())/60
                        prev_time=poll_local

                        if store.status == 'active':
                            uptime+=td
                        else:
                            downtime+=td
                        prev_status = store.status
                    else:
                        # td = ((poll_local - start_time).total_seconds())/60
                        td = (poll_local.hour*60 + poll_local.minute +poll_local.second/60- start_time.hour*60 -start_time.minute -start_time.second/60)
                        prev_time = poll_local

                        if store.status == 'active':
                            uptime+=td
                        else:
                            downtime+=td
                        prev_status = store.status
                else:
                    td=((poll_local-time_one_day_ago_local).total_seconds())/60
                    prev_time = poll_local

                    if store.status == 'active':
                        uptime+=td
                    else:
                        downtime+=td
                    prev_status = store.status

            else:
                if prev_time is not None:
                    if poll_local.time() > end_time and prev_time.time() < end_time:
                        td = ( end_time.hour*60 +end_time.minute +end_time.second/60 -prev_time.hour*60 - prev_time.minute -prev_time.second/60)
                        prev_time = poll_local
                        if prev_status == 'active':
                            uptime+=td
                        else:
                            downtime+=td
                        prev_status = store.status

                    else:
                        prev_time = poll_local
                        continue

                else:
                    prev_time = poll_local
                    continue
                
    return uptime/60,downtime/60

def get_uptime_downtime(db:Session, report_id:str):
    start=datetime.now()
    c=0
    res=[]
    curr_time = datetime.strptime("2023-01-25 18:13:22.47922 UTC", "%Y-%m-%d %H:%M:%S.%f %Z")
    time_one_hour_ago = curr_time - timedelta(hours=1)
    time_one_day_ago = curr_time - timedelta(days=1)


    store_ids=db.query(Timezone.store_id).all()
    store_ids = [store_id for (store_id,) in store_ids]
    a=[]
    for store_id in store_ids:
    
        print(f"store id - {store_id}")
        timezone = get_timezone(db,store_id)
        
        uptime_last_hour,downtime_last_hour = one_hour_ago(db,store_id,timezone,time_one_hour_ago,curr_time)
        uptime_last_day,downtime_last_day= one_day_ago(db,store_id,timezone,time_one_day_ago,curr_time)


        if c==5:
            break
        c+=1
        # break
    print(a)