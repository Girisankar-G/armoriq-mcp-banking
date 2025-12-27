from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine, get_db
from tools.banking_tools import mcp, API_KEY

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ArmorIQ Banking MCP Server")

@app.middleware("http")
async def validate_api_key_middleware(request: Request, call_next):
    # Allow public access to health check and docs
    if request.url.path in ["/", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Secure all other endpoints
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"detail": "Unauthorized: Missing or invalid API Key"}
        )
    
    return await call_next(request)

@app.get("/")
def health_check():
    return {"status": "online", "security": "middleware_active"}

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

app.mount("/mcp", mcp.sse_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)