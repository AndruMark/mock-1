from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user_model import User
from app.schemas.user_schema import UserCreate


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register(db: Session, user_in: UserCreate) -> User:
        hashed_pw = get_password_hash(user_in.password)
        new_user = User(email=user_in.email, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User | None:
        user = AuthService.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
