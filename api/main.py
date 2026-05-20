from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, users, crop_types

"""
App initializer from original class FastAPI
"""

app = FastAPI(
    title="CultivaLab API",
    description="API para una app con el objetivo de "
    "modelar y simular el crecimiento de cultivos",
    version="1.0.0",
)

"""
CORS to allow connection from future FrontEnd
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"Message": "CultivaLab API working tree clean"}


@app.get("/health")
def health():
    return {"Status": "Ok"}

app.include_router(auth.router)
app.include_router(users.router)
