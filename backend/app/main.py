from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.dashboard import router as dashboard_router
from app.routers.products import router as products_router
from app.routers.user_actions import router as user_actions_router

app = FastAPI(title="Novera API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router)
app.include_router(dashboard_router)
app.include_router(user_actions_router)


@app.get("/")
def root():
    return {"message": "Novera backend is running"}