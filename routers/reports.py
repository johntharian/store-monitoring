from fastapi import APIRouter,Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
from utils import services

router = APIRouter()

# @DESC - reuturns report_id that will be used for polling the status of report completion
# @ROUTE - GET
# @PARAMS - NONE
@router.get('/trigger_report')
async def trigger_report(db:Session = Depends(get_db)): 
    return services.trigger_report(db)

@router.get('/get_report/{report_id}')
async def get_report(report_id:str, db:Session = Depends(get_db)):
    return services.get_report(db,report_id)