from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.category_service import get_category_or_404


def list_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 50) -> list[Expense]:
    return (
        db.query(Expense)
        .filter(Expense.user_id == user_id)
        .order_by(Expense.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_expense(db: Session, user_id: int, data: ExpenseCreate) -> Expense:
    get_category_or_404(db, user_id, data.category_id)
    expense = Expense(
        amount=data.amount,
        description=data.description,
        date=data.date,
        category_id=data.category_id,
        user_id=user_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expense_or_404(db: Session, user_id: int, expense_id: int) -> Expense:
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == user_id).first()
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense


def update_expense(db: Session, user_id: int, expense_id: int, data: ExpenseUpdate) -> Expense:
    expense = get_expense_or_404(db, user_id, expense_id)
    if data.category_id is not None:
        get_category_or_404(db, user_id, data.category_id)
        expense.category_id = data.category_id
    for field in ("amount", "description", "date"):
        value = getattr(data, field)
        if value is not None:
            setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, user_id: int, expense_id: int) -> None:
    expense = get_expense_or_404(db, user_id, expense_id)
    db.delete(expense)
    db.commit()
