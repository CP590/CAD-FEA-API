from fastapi import FastAPI
from api import endpoints
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:4200"]

app.include_router(endpoints.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


@app.get("/")
def read_root():
    return {"message": "Welcome to the CAD FEA API"}
