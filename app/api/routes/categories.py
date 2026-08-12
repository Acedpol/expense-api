from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
def list_categories(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[CategoryRead]:
    return category_service.list_categories(db, current_user.id)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    return category_service.create_category(db, current_user.id, data)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    return category_service.get_category_or_404(db, current_user.id, category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CategoryRead:
    return category_service.update_category(db, current_user.id, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    category_service.delete_category(db, current_user.id, category_id)
