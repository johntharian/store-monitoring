from threading import Thread

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from models.models import Reports
from .report_optimized import get_uptime_downtime

# from .report import get_uptime_downtime_last_hour, get_uptime_downtime_last_day, get_uptime_downtime


def create_report(db: Session, report_id: str):
    """
    Create a report with the given data

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report to create
    """
    report_location = f"reports/{report_id}.csv"
    db_report = Reports(
        report_id=report_id, status="Running", report_location=report_location
    )

    db.add(db_report)
    db.commit()
    db.refresh(db_report)


def trigger_report(db):
    """
    Trigger the creation of a new report.

    Parameters
    ----------
    db : Session
        database session

    Returns
    -------
    str 
        the id of the new report
    """
    report_ids = db.query(Reports.report_id).all()

    report_id = "report" + str(len(report_ids) + 1)
    # data_location="reports"
    create_report(db, report_id)
    daemon = Thread(target=generate_report, args=(db, report_id), daemon=True)
    daemon.start()
    return report_id


def generate_report(db: Session, report_id: str):
    """
    Generates the report.

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report
    """
    # get_uptime_downtime_last_day(db,report_id)
    get_uptime_downtime(db, report_id)
    # get_uptime_downtime_last_hour(db,report_id)
    update_report_status(db, report_id)


def get_report(db: Session, report_id: str):
    """
    Get report from database.

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report to retrieve

    Returns
    -------
    str 
        status of the report
    """
    report = db.query(Reports).filter(Reports.report_id == report_id).first()
    if not report:
        return "No such report id"
    if report.status != "Complete":
        return "Running"
    else:
        file_path = f"reports/{report_id}.csv"
        return FileResponse(
            file_path,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment"},
        )
        # return report


def update_report_status(db: Session, report_id: str):
    """
    Updates status of the report when finished generating.

    Parameters
    ----------
    db : Session
        database session
    report_id : str
        id of the report to retrieve
    """
    report = db.query(Reports).filter(Reports.report_id == report_id).first()

    if report:
        report.status = "Complete"
        print("status updated")
        db.commit()
