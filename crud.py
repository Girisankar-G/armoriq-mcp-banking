from sqlalchemy.orm import Session

# Relative imports
from . import models, schemas


def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()


def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(
        owner_name=account.owner_name,
        balance=account.initial_balance  # FIXED: schema field
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def update_balance(db: Session, account_id: int, amount: float, transaction_type: str):
    account = get_account(db, account_id)  # FIXED: correct function call
    if not account:
        return None

    account.balance += amount

    transaction = models.Transaction(
        account_id=account_id,
        type=transaction_type,
        amount=abs(amount)
    )

    db.add(transaction)
    db.commit()
    db.refresh(account)
    return account


def get_transactions(db: Session, account_id: int):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id)
        .all()
    )
