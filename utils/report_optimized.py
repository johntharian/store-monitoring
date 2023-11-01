from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import pandas as pd
import pytz
from sqlalchemy import asc
from sqlalchemy.orm import Session

from models.models import Stores, BusinessHours, Timezone, Reports


def get_timezone(db: Session, store_id: str):
    """
    Get timezone of a store from database.

    Parameters
    ----------
    db : Session
        database session
    store_id : str
        id of the store to get the timezone

    Returns
    -------
    str
        timezone of the store
    """
    timezone = db.query(Timezone).filter(Timezone.store_id == store_id).first()
    if not timezone:
        timezone = "America/Chicago"
    else:
        timezone = timezone.timezone_str
    return timezone


def get_local(utc_datetime: datetime, timezone: str):
    """
    Convert utc_datetime to local time of a store.

    Parameters
    ----------
    db : Session
        database session
    timzone : str
        timezone to convert to

    Returns
    -------
    datetime
        datetime that is converted to the required time zone
    """
    utc_timezone = pytz.utc
    timezone = pytz.timezone(timezone)
    # convert utc timezone to local time zone
    t = utc_timezone.localize(utc_datetime).astimezone(timezone)
    return t


def get_start_end_time(db: Session, store_id: str, day: int):
    """
    Get opening and closing time of a store for a prticular day.

    Parameters
    ----------
    db : Session
        database session
    store_id : str
        id of the store
    day: int
        day to get the opening and closing time

    Returns
    -------
    tuple
        a tuple containing the opening and closing time for a day
    """
    time = (
        db.query(BusinessHours)
        .filter(BusinessHours.store_id == store_id, BusinessHours.day == day)
        .first()
    )

    start_time = time.start_time_local
    end_time = time.end_time_local

    return start_time, end_time


def update_report_status(db: Session, report_id: str):
    """
    Update the status of the report.

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report to be updated
    """
    report = db.query(Reports).filter(Reports.report_id == report_id).first()

    if report:
        report.status = "Complete"
        db.commit()


def get_uptime_downtime_last_hour(
    db: Session,
    store_id: str,
    timezone: str,
    time_one_hour_ago: datetime,
    curr_time: datetime,
):
    """
    Get uptime and downtime of a store for the last hour.

    Parameters
    ----------
    db : Session
        database session
    store_id : str
        id of the store
    timezone : str
        timezone of the store
    time_one_hour_ago : datetime
        datetime one hour ago
    curr_time : datetime
        current datetime

    Returns
    -------
    tuple
        a tuple containing the uptime and downtime for the last hour
    """
    uptime = 0
    downtime = 0
    prev_time = None
    prev_status = None

    end = 0
    # store data within current time and time_one_hour_ago
    store_data = (
        db.query(Stores)
        .filter(
            Stores.store_id == store_id,
            Stores.timestamp_utc > time_one_hour_ago,
            Stores.timestamp_utc < curr_time,
        )
        .order_by(asc(Stores.timestamp_utc))
        .all()
    )

    # convert current time and time_one_hour_ago to current time
    curr_time_local = get_local(curr_time, timezone)
    time_one_hour_ago_local = curr_time_local - timedelta(hours=1)

    day = curr_time_local.weekday()
    start_time, end_time = get_start_end_time(db, store_id, day)

    if len(store_data) > 0:
        # iterate over each poll data
        for store in store_data:
            poll = store.timestamp_utc
            poll_local = get_local(poll, timezone)

            if prev_time is not None:
                # if poll time is within clsoing time -> calculate time difference
                if poll_local.time() < end_time:
                    # print(poll_local.time(),"here")
                    td = ((poll_local - prev_time).total_seconds()) / 60

                    prev_time = poll_local

                    if store.status == "active":
                        uptime += td
                    else:
                        downtime += td
                    prev_status = store.status

                else:
                    # varabile for checking if time difference between last poll and current time or closing time has been calculated
                    end = 1
                    td = ((curr_time_local - prev_time).total_seconds()) / 60

                    if prev_status == "active":
                        uptime += td
                    else:
                        downtime += td

            else:
                # poll time within store timings
                if start_time <= poll_local.time() <= end_time:
                    td = ((poll_local - time_one_hour_ago_local).total_seconds()) / 60

                    prev_time = poll_local

                    if store.status == "active":
                        uptime += td
                        # prev status
                    else:
                        downtime += td
                        # prev staus

                    prev_status = store.status
                else:
                    end = 1

        if end == 0:
            td = ((curr_time_local - prev_time).total_seconds()) / 60

            if prev_status == "active":
                uptime += td
            else:
                downtime += td

    return uptime, downtime


def get_uptime_downtime_for_day_and_week(
    db: Session, entity: str, store_id: str, timezone: str, curr_time: datetime
):
    """
    Get uptime and downtime of a store for the last day or week.

    Parameters
    ----------
    db : Session
        database session
    entity : str
        field to specify if it is day or week
    store_id : str
        id of the store
    timezone : str
        timezone of the store
    curr_time : datetime
        current datetime

    Returns
    -------
    tuple
        a tuple containing the uptime and downtime for the last day or week
    """

    curr_time_local = get_local(curr_time, timezone)

    # check if day or week to be calculated
    if entity == "day":
        time = curr_time - timedelta(days=1)
        time_local = curr_time_local - timedelta(days=1)
    else:
        time = curr_time - timedelta(weeks=1)
        time_local = curr_time_local - timedelta(weeks=1)

    uptime = 0
    downtime = 0
    prev_time = None
    prev_status = None

    timezone = get_timezone(db, store_id)

    # retrieve store data for the given store and enitity
    store_data = (
        db.query(Stores)
        .filter(
            Stores.store_id == store_id,
            Stores.timestamp_utc > time,
            Stores.timestamp_utc < curr_time,
        )
        .order_by(asc(Stores.timestamp_utc))
        .all()
    )

    if len(store_data) > 0:
        # iterate over each poll
        for store in store_data:
            poll = store.timestamp_utc
            # convert to local time
            poll_local = get_local(poll, timezone)

            poll_day = poll_local.weekday()

            start_time, end_time = get_start_end_time(db, store_id, poll_day)

            # if poll time within store timing
            if start_time <= poll_local.time() <= end_time:
                # check if there is a prev time
                if prev_time is not None:
                    # if prev time is greater than start time -> time difference should be between poll time and prev time
                    if prev_time.time() > start_time:
                        td = ((poll_local - prev_time).total_seconds()) / 60
                        prev_time = poll_local

                        if store.status == "active":
                            uptime += td
                        else:
                            downtime += td
                        prev_status = store.status
                    else:
                        # td = ((poll_local - start_time).total_seconds())/60
                        td = (
                            poll_local.hour * 60
                            + poll_local.minute
                            + poll_local.second / 60
                            - start_time.hour * 60
                            - start_time.minute
                            - start_time.second / 60
                        )
                        prev_time = poll_local

                        if store.status == "active":
                            uptime += td
                        else:
                            downtime += td
                        prev_status = store.status
                else:
                    # poll time is within store timing 
                    td = ((poll_local - time_local).total_seconds()) / 60
                    prev_time = poll_local

                    if store.status == "active":
                        uptime += td
                    else:
                        downtime += td
                    prev_status = store.status

            else:
                if prev_time is not None:
                    # time difference between end time and previous time
                    if poll_local.time() > end_time and prev_time.time() < end_time:
                        td = (
                            end_time.hour * 60
                            + end_time.minute
                            + end_time.second / 60
                            - prev_time.hour * 60
                            - prev_time.minute
                            - prev_time.second / 60
                        )
                        prev_time = poll_local
                        if prev_status == "active":
                            uptime += td
                        else:
                            downtime += td
                        prev_status = store.status

                    else:
                        prev_time = poll_local
                        continue

                else:
                    prev_time = poll_local
                    continue
    # uptime, downtime in minutes to hours
    return uptime / 60, downtime / 60


def get_uptime_downtime(db: Session, report_id: str):
    """
    Get uptime and downtime of a store for a store.

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report to save data to
    """

    start = datetime.now()
    c = 0
    res = []
    # hard coded current time
    curr_time = datetime.strptime(
        "2023-01-25 18:13:22.47922 UTC", "%Y-%m-%d %H:%M:%S.%f %Z"
    )
    time_one_hour_ago = curr_time - timedelta(hours=1)
    # time_one_day_ago = curr_time - timedelta(days=1)

    store_ids = db.query(Timezone.store_id).all()
    store_ids = [store_id for (store_id,) in store_ids]

    # iterate over each store_id
    for store_id in store_ids:
        print(f"store id - {store_id}")
        timezone = get_timezone(db, store_id)

        # added multi threading to decrease compute time
        with ThreadPoolExecutor() as executor:
            future1 = executor.submit(
                get_uptime_downtime_last_hour,
                db,
                store_id,
                timezone,
                time_one_hour_ago,
                curr_time,
            )
            future2 = executor.submit(
                get_uptime_downtime_for_day_and_week,
                db,
                "day",
                store_id,
                timezone,
                curr_time,
            )
            future3 = executor.submit(
                get_uptime_downtime_for_day_and_week,
                db,
                "week",
                store_id,
                timezone,
                curr_time,
            )

            uptime_last_hour, downtime_last_hour = future1.result()
            uptime_last_day, downtime_last_day = future2.result()
            uptime_last_week, downtime_last_week = future3.result()

        # uptime_last_hour,downtime_last_hour = get_uptime_downtime_last_hour(db,store_id,timezone,time_one_hour_ago,curr_time)
        # uptime_last_day,downtime_last_day= get_uptime_downtime_for_day_and_week(db,"day",store_id,timezone,curr_time)
        # uptime_last_week,downtime_last_week= get_uptime_downtime_for_day_and_week(db,"week",store_id,timezone,curr_time)

        res.append(
            {
                "store_id": store_id,
                "uptime_last_hour": uptime_last_hour,
                "uptime_last_day": uptime_last_day,
                "uptime_last_week": uptime_last_week,
                "downtime_last_hour": downtime_last_hour,
                "downtime_last_day": downtime_last_day,
                "downtime_last_week": downtime_last_week,
            }
        )
        # code to break the iteration after a fixed number of store_ids
        if c == 100:
            break
        c += 1
        # break
    # save df to csv
    pd.DataFrame(res).to_csv(f"reports/{report_id}.csv")
    print("Saved to csv")
    end = datetime.now()
    print("Elapsed", (end - start).total_seconds() * 10**6, "µs")
