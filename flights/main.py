from fastapi import FastAPI

from flights.api import views


api = FastAPI()
api.include_router(views.router)
