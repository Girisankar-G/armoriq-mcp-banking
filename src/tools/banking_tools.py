import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

# ✅ RELATIVE IMPORTS (CRITICAL FIX)
from ..database import SessionLocal
from .. import crud, schemas

# Load environment variables
load_dotenv()

API_KEY = os.getenv("MCP_API_KEY")

if not API_KEY:
    raise RuntimeError("MCP_API_KEY not found in .env file")

mcp = FastMCP("ArmorIQ-Banking-Tools")

# ---------- Input Schemas ----------

class AuthBase(BaseModel):
    api_key: str = Field(..., description="API key for tool authorization")

class CreateAccountInput(AuthBase):
    name: str = Field(..., min_length=1, max_length=50)
    initial_deposit: float = Field(default=0.0, ge=0)

class AccountLookupInput(AuthBase):
    account_id: int = Field(..., ge=1)

# ---------- Authorization ----------

def authorize(api_key: str) -> bool:
    return api_key == API_KEY

# ---------- MCP Tools ----------

@mcp.tool()
def create_new_account(input_data: CreateAccountInput) -> dict:
    """Creates a new bank account securely."""
    if not authorize(input_data.api_key):
        return {"status": "error", "message": "Unauthorized"}

    db = SessionLocal()
    try:
        account = crud.create_account(
            db,
            schemas.AccountCreate(
                owner_name=input_data.name.strip(),
                initial_balance=float(input_data.initial_deposit),
            ),
        )

        return {
            "status": "success",
            "account_id": int(account.id),
            "owner_name": account.owner_name,
        }
    finally:
        db.close()


@mcp.tool()
def check_balance(input_data: AccountLookupInput) -> dict:
    """Returns account balance using structured output."""
    if not authorize(input_data.api_key):
        return {"status": "error", "message": "Unauthorized"}

    db = SessionLocal()
    try:
        account = crud.get_account(db, input_data.account_id)
        if not account:
            return {"status": "error", "message": "Account not found"}

        return {
            "status": "success",
            "account_id": int(account.id),
            "balance": round(float(account.balance), 2),
        }
    finally:
        db.close()
