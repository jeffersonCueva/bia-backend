from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import get_database
from app.routes.accounts import get_accounts_router


def create_app():
    db_ctx = get_database("bia_db")
    client = db_ctx["client"]

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            list(client.list_databases())
            print(f"✅ Connected to MongoDB BIA")
        except Exception as e:
            print("❌ MongoDB connection failed")
            raise e
        yield

    app = FastAPI(title=f" BIA API", lifespan=lifespan)

    app.include_router(get_accounts_router(db_ctx["accounts"]))

    @app.get("/")
    def root():
        return {"server": "bia", "status": "running"}

    return app
