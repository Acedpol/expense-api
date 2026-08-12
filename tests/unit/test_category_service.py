from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import category_service


def test_list_categories_filters_by_user():
    db = MagicMock()
    category_service.list_categories(db, user_id=1)
    db.query.return_value.filter.return_value.all.assert_called_once()


def test_create_category_sets_owner_and_persists():
    db = MagicMock()
    result = category_service.create_category(db, user_id=1, data=CategoryCreate(name="Ocio"))
    assert result.name == "Ocio"
    assert result.user_id == 1
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_get_category_or_404_raises_when_missing():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        category_service.get_category_or_404(db, user_id=1, category_id=99)

    assert exc_info.value.status_code == 404


def test_get_category_or_404_returns_when_found():
    db = MagicMock()
    fake_category = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_category

    result = category_service.get_category_or_404(db, user_id=1, category_id=1)

    assert result is fake_category


def test_update_category_applies_only_provided_fields():
    db = MagicMock()
    fake_category = MagicMock()
    fake_category.name = "Old"
    db.query.return_value.filter.return_value.first.return_value = fake_category

    category_service.update_category(db, user_id=1, category_id=1, data=CategoryUpdate(name="New"))

    assert fake_category.name == "New"
    db.commit.assert_called_once()


def test_update_category_keeps_name_when_not_provided():
    db = MagicMock()
    fake_category = MagicMock()
    fake_category.name = "Old"
    db.query.return_value.filter.return_value.first.return_value = fake_category

    category_service.update_category(db, user_id=1, category_id=1, data=CategoryUpdate())

    assert fake_category.name == "Old"


def test_delete_category_deletes_and_commits():
    db = MagicMock()
    fake_category = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_category

    category_service.delete_category(db, user_id=1, category_id=1)

    db.delete.assert_called_once_with(fake_category)
    db.commit.assert_called_once()
