import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, ChangePasswordRequest
from app.core.security import get_password_hash, verify_password, create_access_token
from app.services.sms_service import get_sms_client


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.sms_client = get_sms_client()

    def send_sms_code(self, phone: str, sms_type: str) -> bool:
        # 开发期固定验证码，生产期应生成随机码并缓存
        code = "123456"
        return self.sms_client.send_code(phone, code, sms_type)

    def register(self, data: RegisterRequest) -> User:
        if self.db.query(User).filter(User.phone == data.phone).first():
            raise ValueError("手机号已注册")

        # 开发期：验证固定验证码
        if data.sms_code != "123456":
            raise ValueError("验证码错误")

        user = User(
            user_id=f"U{uuid.uuid4().hex[:8].upper()}",
            phone=data.phone,
            password_hash=get_password_hash(data.password),
            nickname=data.nickname,
            status=1,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, data: LoginRequest) -> User:
        user = self.db.query(User).filter(User.phone == data.phone).first()
        if not user:
            raise ValueError("用户不存在")

        if data.password:
            if not verify_password(data.password, user.password_hash):
                raise ValueError("密码错误")
        elif data.sms_code:
            if data.sms_code != "123456":
                raise ValueError("验证码错误")
        else:
            raise ValueError("登录方式无效")

        return user

    def change_password(self, user: User, data: ChangePasswordRequest):
        if data.old_password:
            if not verify_password(data.old_password, user.password_hash):
                raise ValueError("旧密码错误")
        elif data.sms_code:
            if data.sms_code != "123456":
                raise ValueError("验证码错误")
        else:
            raise ValueError("验证方式无效")

        user.password_hash = get_password_hash(data.new_password)
        self.db.commit()
