from mcp.server.fastmcp import FastMCP
from database import SessionLocal
import crud, schemas

# Initialize FastMCP for tool registration
mcp = FastMCP("Banking-Tools")

@mcp.tool()
def create_new_account(name: str, initial_deposit: float = 0.0):
    """Creates a new bank account for a user."""
    db = SessionLocal()
    try:
        account_data = schemas.AccountCreate(owner_name=name, initial_balance=initial_deposit)
        new_account = crud.create_account(db, account_data)
        return f"Account created for {name} with ID: {new_account.id}"
    finally:
        db.close()

@mcp.tool()
def check_balance(account_id: int):
    """Retrieves the current balance for a specific account ID."""
    db = SessionLocal()
    try:
        account = crud.get_account(db, account_id)
        if not account:
            return "Account not found."
        return f"Current Balance: ${account.balance}"
    finally:
        db.close()

@mcp.tool()
def process_transaction(account_id: int, amount: float, transaction_type: str):
    """Handles deposits or withdrawals. Use 'Deposit' or 'Withdrawal' as type."""
    db = SessionLocal()
    try:
        if transaction_type.lower() == "withdrawal":
            account = crud.get_account(db, account_id)
            if account and account.balance < amount:
                return "Transaction failed: Insufficient funds."
            crud.update_balance(db, account_id, -amount, "Withdrawal")
        else:
            crud.update_balance(db, account_id, amount, "Deposit")
        
        return f"Successfully processed {transaction_type} of ${amount}."
    finally:
        db.close()

@mcp.tool()
def view_history(account_id: int):
    """Returns a list of recent transactions for the account."""
    db = SessionLocal()
    try:
        history = crud.get_transactions(db, account_id)
        if not history:
            return "No transaction history found."
        return [f"{t.type}: ${t.amount} at {t.timestamp}" for t in history]
    finally:
        db.close()