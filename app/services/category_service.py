from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def list_categories(
    db: Session, user_id: int, skip: int = 0, limit: int = 50
) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    category = Category(name=data.name, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category_or_404(db: Session, user_id: int, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category


def update_category(
    db: Session, user_id: int, category_id: int, data: CategoryUpdate
) -> Category:
    category = get_category_or_404(db, user_id, category_id)
    if data.name is not None:
        category.name = data.name
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user_id: int, category_id: int) -> None:
    category = get_category_or_404(db, user_id, category_id)
    db.delete(category)
    db.commit()
