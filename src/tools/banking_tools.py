from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
# Fix: Remove the dots (..) because database.py is in the same parent folder (src)
from database import SessionLocal
import crud
import schemas

API_KEY = "armoriq_secure_key_2025"

mcp = FastMCP("ArmorIQ-Banking-Tools")

# ---------- Input Schemas (Strict & Typed) ----------

class AuthBase(BaseModel):
    api_key: str = Field(..., description="Security key for tool access")

class CreateAccountInput(AuthBase):
    name: str = Field(..., min_length=1, max_length=50, description="Owner name")
    initial_deposit: float = Field(default=0.0, ge=0)

class AccountLookupInput(AuthBase):
    account_id: int = Field(..., ge=1, description="Bank account ID")

# ---------- Helper Functions ----------

def _authorize(api_key: str):
    if api_key != API_KEY:
        return False
    return True

# ---------- MCP Tools ----------

@mcp.tool()
def create_new_account(input_data: CreateAccountInput) -> dict:
    """
    Securely creates a new bank account.
    Returns structured output to prevent prompt injection.
    """
    if not _authorize(input_data.api_key):
        return {"status": "error", "message": "Unauthorized access"}

    db = SessionLocal()
    try:
        safe_name = input_data.name.strip()

        account = crud.create_account(
            db,
            schemas.AccountCreate(
                owner_name=safe_name,
                initial_balance=float(input_data.initial_deposit),
            ),
        )

        return {
            "status": "success",
            "account_id": int(account.id),
            "owner_name": safe_name,
        }
    finally:
        db.close()


@mcp.tool()
def check_balance(input_data: AccountLookupInput) -> dict:
    """
    Retrieves account balance securely.
    Structured response avoids unescaped variables.
    """
    if not _authorize(input_data.api_key):
        return {"status": "error", "message": "Unauthorized access"}

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
