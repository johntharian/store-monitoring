from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from utils import services

router = APIRouter()

# @DESC - returns report_id that will be used for polling the status of report completion
# @ROUTE - GET /trigger_report
# @PARAMS - NONE
@router.get("/trigger_report")
async def trigger_report(db: Session = Depends(get_db)):
    return services.trigger_report(db)


# @DESC - returns status with csv for report_id
# @ROUTE - GET /get_report
# @PARAMS - report_id - id of the report
@router.get("/get_report/{report_id}")
async def get_report(report_id: str, db: Session = Depends(get_db)):
    return services.get_report(db, report_id)
