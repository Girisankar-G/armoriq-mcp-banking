import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
import models
import schemas
import crud
from database import engine, get_db

# ---------------- ENV ----------------

load_dotenv()
API_KEY = os.getenv("MCP_API_KEY")

if not API_KEY:
    raise RuntimeError("MCP_API_KEY not found in .env")

# ---------------- DB ----------------

models.Base.metadata.create_all(bind=engine)

# ---------------- APP ----------------

app = FastAPI(
    title="ArmorIQ Banking MCP Server",
    version="0.1.0"
)

# ---------------- API KEY (Swagger compatible) ----------------

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized: Missing or invalid API Key"
        )

# ---------------- ROUTES ----------------

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.post(
    "/accounts/",
    response_model=schemas.Account,
    dependencies=[Depends(verify_api_key)]
)
def create_account(
    account: schemas.AccountCreate,
    db: Session = Depends(get_db)
):
    return crud.create_account(db, account)

@app.get(
    "/accounts/{account_id}",
    response_model=schemas.Account,
    dependencies=[Depends(verify_api_key)]
)
def get_account(
    account_id: int,
    db: Session = Depends(get_db)
):
    acc = crud.get_account(db, account_id)
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@app.post(
    "/accounts/{account_id}/deposit",
    response_model=schemas.Account,
    dependencies=[Depends(verify_api_key)]
)
def deposit(
    account_id: int,
    update: schemas.UpdateBalance,
    db: Session = Depends(get_db)
):
    acc = crud.update_balance(db, account_id, update.amount, "deposit")
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@app.post(
    "/accounts/{account_id}/withdraw",
    response_model=schemas.Account,
    dependencies=[Depends(verify_api_key)]
)
def withdraw(
    account_id: int,
    update: schemas.UpdateBalance,
    db: Session = Depends(get_db)
):
    acc = crud.update_balance(db, account_id, -update.amount, "withdraw")
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")
    return acc

@app.get(
    "/accounts/{account_id}/transactions",
    response_model=list[schemas.Transaction],
    dependencies=[Depends(verify_api_key)]
)
def transactions(
    account_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_transactions(db, account_id)
