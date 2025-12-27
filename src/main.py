from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db
from tools.banking_tools import mcp

# Initialize database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ArmorIQ Banking MCP Server",
    description="A secure banking service with integrated MCP tools.",
    version="1.0.0"
)

# --- Standard API Endpoints ---

@app.get("/")
def health_check():
    return {
        "status": "online", 
        "mcp_enabled": True,
        "mcp_path": "/mcp/sse"
    }

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    return crud.create_account(db, account)

@app.get("/accounts/{account_id}", response_model=schemas.Account)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = crud.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/accounts/{account_id}/deposit", response_model=schemas.Account)
def deposit(account_id: int, update: schemas.UpdateBalance, db: Session = Depends(get_db)):
    return crud.update_balance(db, account_id, update.amount, "DEPOSIT")

@app.post("/accounts/{account_id}/withdraw", response_model=schemas.Account)
def withdraw(account_id: int, update: schemas.UpdateBalance, db: Session = Depends(get_db)):
    account = crud.get_account(db, account_id)
    if not account or account.balance < update.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    return crud.update_balance(db, account_id, -update.amount, "WITHDRAWAL")

@app.get("/accounts/{account_id}/transactions", response_model=List[schemas.Transaction])
def transaction_history(account_id: int, db: Session = Depends(get_db)):
    return crud.get_transactions(db, account_id)

# --- MCP Protocol Mounting ---
# Based on your dir() output, sse_app is the valid Starlette app for MCP
app.mount("/mcp", mcp.sse_app)

if __name__ == "__main__":
    import uvicorn
    # Using string format for uvicorn is essential for reload on Windows
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)