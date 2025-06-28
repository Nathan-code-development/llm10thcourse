from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.db.session import get_session
from app.models.user import User, UserCreate


def authenticate_user(username: str, password: str) -> User | None:
    """
    验证用户凭据并返回用户对象
    """
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


def register_user(user_in: UserCreate) -> User | None:
    """
    注册新用户
    """
    with get_session() as db:
        # 检查用户名是否已存在
        existing_user = db.exec(
            select(User).where(User.username == user_in.username)
        ).first()
        if existing_user:
            return None

        # 检查邮箱是否已存在
        existing_email = db.exec(
            select(User).where(User.email == user_in.email)
        ).first()
        if existing_email:
            return None

        # 创建新用户
        hashed_password = get_password_hash(user_in.password)
        user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            role=user_in.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user 