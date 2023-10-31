from pydantic import BaseModel
from datetime import datetime,time

class Stores(BaseModel):
    store_id : int
    timestamp_utc: datetime
    status : str

    class Config:
        orm_mode = True

class BusinessHours(BaseModel):
    store_id : int
    day : int
    start_time_local : time
    end_time_local  : time

    class Config:
        orm_mode = True

class Timezone(BaseModel):
    store_id : int
    timezone_str : str

    class Config:
        orm_mode = True

class Reports(BaseModel):
    report_id : str
    status : str
    report_location : str

    class Config:
        orm_mode = True