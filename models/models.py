from sqlalchemy import (
    BigInteger,
    Column,
    Integer,
    String,
    TIMESTAMP,
    Time,
)

# from sqlalchemy.orm import relationship

from database import Base

# store model
class Stores(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(BigInteger, index=True)
    timestamp_utc = Column(TIMESTAMP)
    status = Column(String)

    # timezone = relationship("Timezone", back_populates="stores")

# businessHour model
class BusinessHours(Base):
    __tablename__ = "businessHours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(BigInteger, index=True)
    day = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)

    # timezone = relationship("Timezone", back_populates="business_hours")

# timezone model
class Timezone(Base):
    __tablename__ = "timezone"

    store_id = Column(BigInteger, primary_key=True, unique=True, index=True)
    timezone_str = Column(String, index=True)

    # stores = relationship("Stores", back_populates="timezone")
    # business_hours = relationship("BusinessHours", back_populates="timezone")

# report model
class Reports(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    report_id = Column(String, unique=True, index=True)
    status = Column(String, index=True)
    report_location = Column(String, index=True)
