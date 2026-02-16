from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
import uuid

# -------------------- Main router --------------------
def get_accounts_router(accounts_collection, banks_collection=None):
    """
    Returns a router for account operations:
    - Check balance
    - Get bank-specific accounts
    - Onboard client
    """
    router = APIRouter(prefix="/accounts", tags=["Accounts"])

    # -------------------- Existing: Check balance --------------------
    @router.get("/{account_id}")
    async def get_bank_accounts(account_id: str):
        acc = await accounts_collection.find_one(
            {"account_id": account_id},
        )

        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")

        return acc

    # -------------------- Existing: Bank-specific account --------------------
    @router.get("/bank/{account_id}/{bank}")
    async def get_bank_account_id(account_id: str, bank: str):
        bank = bank.lower()
        acc = await accounts_collection.find_one(
            {"account_id": account_id},
        )

        for item in acc.get("banks", []):
            if bank in item:
                return item[bank]

        return "account Doesnt Exist"

    # -------------------- New: Client Onboarding --------------------
    @router.post("/onboard_client")
    async def onboard_client(client: dict):
        """
        Onboards a new client into the accounts collection.
        Required fields: fullName, email, mobile
        """
        required = ["fullName", "email", "mobile"]
        for r in required:
            if not client.get(r):
                raise HTTPException(status_code=400, detail=f"{r} is required.")

        # Check if client already exists
        existing = await accounts_collection.find_one({"email": client["email"]})
        if existing:
            raise HTTPException(status_code=400, detail="Client already exists.")

        new_client = {
            "userId": f"USER-{uuid.uuid4().hex[:6]}",
            "fullName": client["fullName"],
            "email": client["email"],
            "mobile": client["mobile"],
            "createdAt": datetime.utcnow().isoformat(),
            "status": "active",
            "banks": []  # Optional, can store connected banks later
        }

        await accounts_collection.insert_one(new_client)

        return {"status": "success", "client": new_client}

    # -------------------- Optional: Check balance per bank --------------------
    @router.get("/balance/{account_id}/{bank_name}")
    async def check_balance(account_id: str, bank_name: str):
        account_id = account_id.upper()
        bank_name = bank_name.lower()
        acc = await accounts_collection.find_one(
            {"account_id": account_id, "bank_name": bank_name}, {"_id": 0}
        )

        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")

        return acc

    return router
