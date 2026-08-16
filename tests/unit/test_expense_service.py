from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services import expense_service


def test_list_expenses_paginates_and_orders():
    db = MagicMock()
    expense_service.list_expenses(db, user_id=1, skip=10, limit=5)

    offset_call = db.query.return_value.filter.return_value.order_by.return_value.offset
    offset_call.assert_called_once_with(10)
    offset_call.return_value.limit.assert_called_once_with(5)


@patch("app.services.expense_service.get_category_or_404")
def test_create_expense_validates_category_belongs_to_user(mock_get_category):
    db = MagicMock()
    data = ExpenseCreate(
        amount=12.5, description="Cafe", date=date(2026, 1, 1), category_id=5
    )

    result = expense_service.create_expense(db, user_id=1, data=data)

    mock_get_category.assert_called_once_with(db, 1, 5)
    assert result.description == "Cafe"
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()


@patch("app.services.expense_service.get_category_or_404")
def test_create_expense_propagates_404_for_foreign_category(mock_get_category):
    mock_get_category.side_effect = HTTPException(
        status_code=404, detail="Category not found"
    )
    db = MagicMock()
    data = ExpenseCreate(
        amount=12.5, description="Cafe", date=date(2026, 1, 1), category_id=999
    )

    with pytest.raises(HTTPException) as exc_info:
        expense_service.create_expense(db, user_id=1, data=data)

    assert exc_info.value.status_code == 404
    db.add.assert_not_called()


def test_get_expense_or_404_raises_when_missing():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        expense_service.get_expense_or_404(db, user_id=1, expense_id=1)

    assert exc_info.value.status_code == 404


@patch("app.services.expense_service.get_category_or_404")
def test_update_expense_revalidates_new_category_ownership(mock_get_category):
    db = MagicMock()
    fake_expense = MagicMock(category_id=1)
    db.query.return_value.filter.return_value.first.return_value = fake_expense

    expense_service.update_expense(
        db, user_id=1, expense_id=1, data=ExpenseUpdate(category_id=2)
    )

    mock_get_category.assert_called_once_with(db, 1, 2)
    assert fake_expense.category_id == 2


def test_update_expense_only_touches_provided_fields():
    db = MagicMock()
    fake_expense = MagicMock(amount=10, description="Old", date=date(2026, 1, 1))
    db.query.return_value.filter.return_value.first.return_value = fake_expense

    expense_service.update_expense(
        db, user_id=1, expense_id=1, data=ExpenseUpdate(description="New")
    )

    assert fake_expense.description == "New"
    assert fake_expense.amount == 10


def test_delete_expense_deletes_and_commits():
    db = MagicMock()
    fake_expense = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_expense

    expense_service.delete_expense(db, user_id=1, expense_id=1)

    db.delete.assert_called_once_with(fake_expense)
    db.commit.assert_called_once()
