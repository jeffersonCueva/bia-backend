from fastapi import APIRouter, HTTPException
from bson import ObjectId


def get_accounts_router(accounts_collection):
    router = APIRouter(prefix="/account", tags=["Accounts"])

    @router.get("/{account_id}")
    async def get_bank_accounts(account_id: str):
        acc = await accounts_collection.find_one(
            {
                "account_id": account_id,
            }
        )
        # print(acc)

        if not acc:
            raise HTTPException(status_code=404, detail="Account not found")

        return acc

    @router.get("/bank/{account_id}/{bank}")
    async def get_bank_account_id(account_id: str, bank: str):
        bank = bank.lower()
        acc = await accounts_collection.find_one(
            {
                "account_id": account_id,
            },
        )

        print(acc["banks"])
        for item in acc.get("banks", []):
            if bank in item:
                return item[bank]
        return "account Doesnt Exist"

    return router
