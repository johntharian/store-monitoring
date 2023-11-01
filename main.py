from fastapi import FastAPI
import uvicorn

from database import engine
from models import models
from routers import reports, data

# database connection
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

# routes
app.include_router(reports.router)
app.include_router(data.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
