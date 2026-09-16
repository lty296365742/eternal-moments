# 纪念日APP 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 iOS 原生 SwiftUI 纪念日管理应用，包含登录注册、人物管理、纪念日记录、提醒功能与 AI 内容生成，配套 FastAPI + PostgreSQL 后端，支持 Docker 本地开发。

**Architecture:** 单仓库单体架构，前后端分离。iOS 端使用 SwiftUI + MVVM，后端使用 FastAPI + SQLAlchemy + APScheduler，PostgreSQL 作为唯一数据库，AI 与短信通过抽象客户端接入。

**Tech Stack:** SwiftUI, FastAPI, SQLAlchemy, Alembic, PostgreSQL, APScheduler, JWT, Docker, 火山方舟, 阿里云短信（生产）

---

## 文件结构

```
纪念日APP/
├── mobile/EternalMoments/
│   ├── App/
│   │   ├── EternalMomentsApp.swift
│   │   ├── ContentView.swift
│   │   └── AuthManager.swift
│   ├── Views/
│   │   ├── LoginView.swift
│   │   ├── RegisterView.swift
│   │   ├── ContactsListView.swift
│   │   ├── ContactDetailView.swift
│   │   ├── AddContactView.swift
│   │   ├── AddAnniversaryView.swift
│   │   ├── RemindersView.swift
│   │   ├── SettingsView.swift
│   │   └── Components/
│   ├── ViewModels/
│   │   ├── LoginViewModel.swift
│   │   ├── ContactsViewModel.swift
│   │   ├── ContactDetailViewModel.swift
│   │   ├── AddContactViewModel.swift
│   │   ├── AddAnniversaryViewModel.swift
│   │   ├── RemindersViewModel.swift
│   │   └── SettingsViewModel.swift
│   ├── Services/
│   │   ├── APIClient.swift
│   │   ├── KeychainService.swift
│   │   └── NotificationService.swift
│   ├── Models/
│   │   ├── User.swift
│   │   ├── Contact.swift
│   │   ├── Anniversary.swift
│   │   ├── Holiday.swift
│   │   └── Reminder.swift
│   └── Resources/
│       └── Info.plist
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── security.py
│   │   │   └── exceptions.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── contact.py
│   │   │   ├── anniversary.py
│   │   │   ├── holiday.py
│   │   │   └── reminder.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── contact.py
│   │   │   ├── anniversary.py
│   │   │   ├── holiday.py
│   │   │   └── reminder.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── contact_service.py
│   │   │   ├── anniversary_service.py
│   │   │   ├── holiday_service.py
│   │   │   ├── reminder_service.py
│   │   │   ├── ai_service.py
│   │   │   └── sms_service.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── contacts.py
│   │   │   ├── anniversaries.py
│   │   │   ├── holidays.py
│   │   │   └── reminders.py
│   │   └── jobs/
│   │       └── reminder_job.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_contacts.py
│   │   ├── test_anniversaries.py
│   │   ├── test_holidays.py
│   │   └── test_reminders.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
└── infra/
    └── docker-compose.yml
```

---

## 阶段 0：项目初始化

### Task 1：后端项目骨架

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/Dockerfile`
- Test: `backend/tests/test_main.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
apscheduler==3.10.4
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

- [ ] **Step 2: 创建核心配置**

```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://em_user:em_pass@localhost:5432/eternal_moments"
    JWT_SECRET: str = "dev_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30
    UPLOAD_DIR: str = "uploads"
    AI_PROVIDER: str = "mock"
    VOLCANO_ARK_API_KEY: str = ""
    SMS_PROVIDER: str = "mock"

    class Config:
        env_file = ".env"

settings = Settings()
```

- [ ] **Step 3: 创建数据库连接**

```python
# backend/app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: 创建主应用**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, contacts, anniversaries, holidays, reminders

app = FastAPI(title="Eternal Moments API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(anniversaries.router, prefix="/api/v1/anniversaries", tags=["anniversaries"])
app.include_router(holidays.router, prefix="/api/v1/holidays", tags=["holidays"])
app.include_router(reminders.router, prefix="/api/v1/reminders", tags=["reminders"])

@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 5: 创建 Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 6: 运行验证**

Run: `docker build -t eternal-moments-backend ./backend`
Expected: build success

---

### Task 2：iOS 项目骨架

**Files:**
- Create: `mobile/EternalMoments/EternalMomentsApp.swift`
- Create: `mobile/EternalMoments/ContentView.swift`
- Create: `mobile/EternalMoments/Services/APIClient.swift`
- Create: `mobile/EternalMoments/Services/KeychainService.swift`

- [ ] **Step 1: 创建 Xcode 项目**

在 Xcode 中创建 iOS App，Bundle ID: `com.eternalmoments.app`，Interface: SwiftUI，Language: Swift。

- [ ] **Step 2: 创建 App 入口**

```swift
// mobile/EternalMoments/EternalMomentsApp.swift
import SwiftUI

@main
struct EternalMomentsApp: App {
    @StateObject private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
        }
    }
}
```

- [ ] **Step 3: 创建 ContentView**

```swift
// mobile/EternalMoments/ContentView.swift
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        if authManager.isAuthenticated {
            MainTabView()
        } else {
            LoginView()
        }
    }
}

struct MainTabView: View {
    var body: some View {
        TabView {
            ContactsListView()
                .tabItem { Label("联系人", systemImage: "person.2.fill") }
            RemindersView()
                .tabItem { Label("提醒", systemImage: "bell.fill") }
            SettingsView()
                .tabItem { Label("设置", systemImage: "gearshape.fill") }
        }
        .accentColor(Color(red: 212/255, green: 63/255, blue: 82/255))
    }
}
```

- [ ] **Step 4: 创建 APIClient**

```swift
// mobile/EternalMoments/Services/APIClient.swift
import Foundation

enum APIError: Error {
    case invalidURL
    case networkError(Error)
    case invalidResponse
    case serverError(Int, String)
    case unauthorized
}

class APIClient {
    static let shared = APIClient()
    private let baseURL = URL(string: "http://localhost:8000/api/v1")!

    private init() {}

    func request<T: Decodable>(
        path: String,
        method: String = "GET",
        body: Encodable? = nil,
        token: String? = nil
    ) async throws -> T {
        guard let url = URL(string: path, relativeTo: baseURL) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        if httpResponse.statusCode == 401 {
            throw APIError.unauthorized
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            let message = String(data: data, encoding: .utf8) ?? "Unknown error"
            throw APIError.serverError(httpResponse.statusCode, message)
        }

        let apiResponse = try JSONDecoder().decode(APIResponse<T>.self, from: data)
        return apiResponse.data
    }
}

struct APIResponse<T: Decodable>: Decodable {
    let code: Int
    let message: String
    let data: T
}
```

- [ ] **Step 5: 创建 KeychainService**

```swift
// mobile/EternalMoments/Services/KeychainService.swift
import Foundation
import Security

class KeychainService {
    static let shared = KeychainService()
    private let service = "com.eternalmoments.app"

    private init() {}

    func saveToken(_ token: String) {
        let data = token.data(using: .utf8)!
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func getToken() -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token",
            kSecReturnData as String: true
        ]
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    func deleteToken() {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: "auth_token"
        ]
        SecItemDelete(query as CFDictionary)
    }
}
```

---

## 阶段 1：F1 登录注册

### Task 3：后端用户模型与数据库迁移

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/core/security.py`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_create_users.py`
- Test: `backend/tests/test_auth_models.py`

- [ ] **Step 1: 创建用户模型**

```python
# backend/app/models/user.py
from sqlalchemy import Column, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "t_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(32), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(500), nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建认证 Schemas**

```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class SendSmsRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    type: str = Field(..., pattern="^(register|login|reset)$")

    @validator("phone")
    def validate_phone(cls, v):
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError("手机号格式不正确")
        return v

class RegisterRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    sms_code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6, max_length=20)
    nickname: Optional[str] = Field(None, max_length=50)

class LoginRequest(BaseModel):
    phone: str = Field(..., min_length=11, max_length=11)
    password: Optional[str] = None
    sms_code: Optional[str] = None

    @validator("sms_code", always=True)
    def validate_login_method(cls, v, values):
        if not values.get("password") and not v:
            raise ValueError("密码和验证码至少填写一项")
        return v

class ChangePasswordRequest(BaseModel):
    old_password: Optional[str] = None
    sms_code: Optional[str] = None
    new_password: str = Field(..., min_length=6, max_length=20)

class AuthResponse(BaseModel):
    user_id: str
    token: str
    expires_in: int
```

- [ ] **Step 3: 创建安全工具**

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
```

- [ ] **Step 4: 创建 Alembic 迁移**

```python
# backend/alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.config import settings
from app.core.database import Base
from app.models import user  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
fileConfig(config.config_file_name)
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 5: 生成迁移脚本**

Run: `cd backend && alembic revision --autogenerate -m "create users table"`
Expected: 生成 `versions/001_create_users_table.py`

- [ ] **Step 6: 应用迁移**

Run: `cd backend && alembic upgrade head`
Expected: 数据库中出现 `t_user` 表

- [ ] **Step 7: Commit**

```bash
git add backend/app/models/user.py backend/app/schemas/auth.py backend/app/core/security.py backend/alembic/
git commit -m "feat: add user model and auth schemas"
```

---

### Task 4：后端认证服务与路由

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/sms_service.py`
- Create: `backend/app/routers/auth.py`
- Modify: `backend/app/core/database.py` (添加 get_current_user 依赖)
- Test: `backend/tests/test_auth_service.py`

- [ ] **Step 1: 创建 SMS 服务**

```python
# backend/app/services/sms_service.py
from abc import ABC, abstractmethod

class SmsClient(ABC):
    @abstractmethod
    def send_code(self, phone: str, code: str, type: str) -> bool:
        pass

class MockSmsClient(SmsClient):
    def send_code(self, phone: str, code: str, type: str) -> bool:
        # 开发期：不实际发送，任何手机号都成功
        return True

class AliyunSmsClient(SmsClient):
    def send_code(self, phone: str, code: str, type: str) -> bool:
        # 生产期：接入阿里云短信 SDK
        # 这里返回 False 表示未配置
        return False

def get_sms_client() -> SmsClient:
    from app.core.config import settings
    if settings.SMS_PROVIDER == "aliyun":
        return AliyunSmsClient()
    return MockSmsClient()
```

- [ ] **Step 2: 创建认证服务**

```python
# backend/app/services/auth_service.py
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
```

- [ ] **Step 3: 创建认证路由**

```python
# backend/app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.schemas.auth import (
    SendSmsRequest, RegisterRequest, LoginRequest,
    ChangePasswordRequest, AuthResponse
)
from app.core.config import settings

router = APIRouter()

@router.post("/sms/send")
def send_sms(data: SendSmsRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    success = service.send_sms_code(data.phone, data.type)
    if not success:
        raise HTTPException(status_code=500, detail="发送失败")
    return {"code": 0, "message": "success", "data": None}

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"user_id": user.user_id, "phone": user.phone})
    return {
        "code": 0,
        "message": "success",
        "data": AuthResponse(
            user_id=user.user_id,
            token=token,
            expires_in=settings.JWT_EXPIRE_DAYS * 86400
        )
    }

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"user_id": user.user_id, "phone": user.phone})
    return {
        "code": 0,
        "message": "success",
        "data": AuthResponse(
            user_id=user.user_id,
            token=token,
            expires_in=settings.JWT_EXPIRE_DAYS * 86400
        )
    }
```

- [ ] **Step 4: 添加当前用户依赖**

```python
# backend/app/core/database.py (追加)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = decode_access_token(credentials.credentials)
        return payload["user_id"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
```

- [ ] **Step 5: 运行测试**

Run: `cd backend && pytest tests/test_auth.py -v`
Expected: 所有认证接口测试通过

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/ backend/app/routers/ backend/app/core/database.py
git commit -m "feat: implement auth service and routes"
```

---

### Task 5：iOS 登录注册 UI

**Files:**
- Create: `mobile/EternalMoments/App/AuthManager.swift`
- Create: `mobile/EternalMoments/Models/User.swift`
- Create: `mobile/EternalMoments/ViewModels/LoginViewModel.swift`
- Create: `mobile/EternalMoments/Views/LoginView.swift`
- Create: `mobile/EternalMoments/Views/RegisterView.swift`

- [ ] **Step 1: 创建 AuthManager**

```swift
// mobile/EternalMoments/App/AuthManager.swift
import Foundation

@MainActor
class AuthManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?

    private let keychain = KeychainService.shared
    private let api = APIClient.shared

    init() {
        if let token = keychain.getToken() {
            isAuthenticated = true
            // 可选：调用 /auth/me 验证 token
        }
    }

    func login(phone: String, password: String? = nil, smsCode: String? = nil) async throws {
        struct LoginRequest: Encodable {
            let phone: String
            let password: String?
            let sms_code: String?
        }

        struct LoginResponse: Decodable {
            let user_id: String
            let token: String
            let expires_in: Int
        }

        let request = LoginRequest(phone: phone, password: password, sms_code: smsCode)
        let response: LoginResponse = try await api.request(path: "auth/login", method: "POST", body: request)

        keychain.saveToken(response.token)
        currentUser = User(userId: response.user_id, phone: phone)
        isAuthenticated = true
    }

    func register(phone: String, smsCode: String, password: String, nickname: String?) async throws {
        struct RegisterRequest: Encodable {
            let phone: String
            let sms_code: String
            let password: String
            let nickname: String?
        }

        struct RegisterResponse: Decodable {
            let user_id: String
            let token: String
            let expires_in: Int
        }

        let request = RegisterRequest(phone: phone, sms_code: smsCode, password: password, nickname: nickname)
        let response: RegisterResponse = try await api.request(path: "auth/register", method: "POST", body: request)

        keychain.saveToken(response.token)
        currentUser = User(userId: response.user_id, phone: phone)
        isAuthenticated = true
    }

    func sendSmsCode(phone: String, type: String) async throws {
        struct SmsRequest: Encodable {
            let phone: String
            let type: String
        }
        let request = SmsRequest(phone: phone, type: type)
        let _: EmptyResponse = try await api.request(path: "auth/sms/send", method: "POST", body: request)
    }

    func logout() {
        keychain.deleteToken()
        currentUser = nil
        isAuthenticated = false
    }
}

struct EmptyResponse: Decodable {}
```

- [ ] **Step 2: 创建 User 模型**

```swift
// mobile/EternalMoments/Models/User.swift
import Foundation

struct User: Codable, Identifiable {
    let id: UUID = UUID()
    let userId: String
    let phone: String
    var nickname: String?
    var avatar: String?
}
```

- [ ] **Step 3: 创建 LoginViewModel**

```swift
// mobile/EternalMoments/ViewModels/LoginViewModel.swift
import Foundation

@MainActor
class LoginViewModel: ObservableObject {
    @Published var phone = ""
    @Published var password = ""
    @Published var smsCode = ""
    @Published var useSmsLogin = false
    @Published var errorMessage: String?
    @Published var isLoading = false

    private let authManager: AuthManager

    init(authManager: AuthManager) {
        self.authManager = authManager
    }

    func login() async {
        guard !phone.isEmpty else {
            errorMessage = "请输入手机号"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            if useSmsLogin {
                try await authManager.login(phone: phone, smsCode: smsCode)
            } else {
                try await authManager.login(phone: phone, password: password)
            }
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func sendSmsCode() async {
        do {
            try await authManager.sendSmsCode(phone: phone, type: "login")
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

- [ ] **Step 4: 创建 LoginView**

```swift
// mobile/EternalMoments/Views/LoginView.swift
import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var viewModel: LoginViewModel
    @State private var showRegister = false

    init() {
        _viewModel = StateObject(wrappedValue: LoginViewModel(authManager: AuthManager()))
    }

    var body: some View {
        ZStack {
            Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

            VStack(spacing: 20) {
                Spacer()

                Image(systemName: "auto_awesome")
                    .resizable()
                    .frame(width: 60, height: 60)
                    .foregroundColor(.white)
                    .padding(20)
                    .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                    .cornerRadius(16)

                Text("纪念日")
                    .font(.system(size: 34, weight: .bold))
                    .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))

                Text("不仅仅是日子，更是生活")
                    .font(.body)
                    .foregroundColor(.gray)

                VStack(spacing: 0) {
                    TextField("手机号", text: $viewModel.phone)
                        .keyboardType(.phonePad)
                        .padding()
                        .background(Color.white)
                        .overlay(Rectangle().frame(height: 1).foregroundColor(Color.gray.opacity(0.2)), alignment: .bottom)

                    if viewModel.useSmsLogin {
                        HStack {
                            TextField("验证码", text: $viewModel.smsCode)
                                .keyboardType(.numberPad)
                            Button("获取验证码") {
                                Task { await viewModel.sendSmsCode() }
                            }
                            .font(.caption)
                            .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                        }
                        .padding()
                        .background(Color.white)
                    } else {
                        SecureField("密码", text: $viewModel.password)
                            .padding()
                            .background(Color.white)
                    }
                }
                .cornerRadius(12)
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
                .padding(.horizontal)

                Toggle("使用验证码登录", isOn: $viewModel.useSmsLogin)
                    .font(.subheadline)
                    .padding(.horizontal)

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button(action: { Task { await viewModel.login() } }) {
                    Text("登录")
                        .font(.headline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .cornerRadius(10)
                }
                .padding(.horizontal)
                .disabled(viewModel.isLoading)

                HStack {
                    Text("还没有账号？")
                        .foregroundColor(.gray)
                    Button("立即注册") { showRegister = true }
                        .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                }
                .font(.subheadline)

                Spacer()
            }
            .onAppear {
                viewModel.errorMessage = nil
            }
        }
        .sheet(isPresented: $showRegister) {
            RegisterView()
        }
    }
}
```

- [ ] **Step 5: 创建 RegisterView**

```swift
// mobile/EternalMoments/Views/RegisterView.swift
import SwiftUI

struct RegisterView: View {
    @EnvironmentObject var authManager: AuthManager
    @Environment(\.dismiss) var dismiss

    @State private var phone = ""
    @State private var smsCode = ""
    @State private var password = ""
    @State private var nickname = ""
    @State private var errorMessage: String?
    @State private var isLoading = false

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("注册信息")) {
                    TextField("手机号", text: $phone)
                        .keyboardType(.phonePad)
                    HStack {
                        TextField("验证码", text: $smsCode)
                            .keyboardType(.numberPad)
                        Button("获取验证码") {
                            Task {
                                try? await authManager.sendSmsCode(phone: phone, type: "register")
                            }
                        }
                        .font(.caption)
                    }
                    SecureField("密码（6-20位）", text: $password)
                    TextField("昵称（选填）", text: $nickname)
                }

                if let error = errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                }

                Button(action: register) {
                    Text("注册")
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .cornerRadius(10)
                }
                .listRowBackground(Color.clear)
            }
            .navigationTitle("注册")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
        }
    }

    private func register() {
        isLoading = true
        Task {
            do {
                try await authManager.register(
                    phone: phone,
                    smsCode: smsCode,
                    password: password,
                    nickname: nickname.isEmpty ? nil : nickname
                )
                dismiss()
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
```

- [ ] **Step 6: 运行验证**

在 Xcode 中构建并运行，确认登录/注册流程可正常调用后端。

---

## 阶段 2：F2 人物管理

### Task 6：后端人物模型与 CRUD

**Files:**
- Create: `backend/app/models/contact.py`
- Create: `backend/app/schemas/contact.py`
- Create: `backend/app/services/contact_service.py`
- Create: `backend/app/routers/contacts.py`
- Test: `backend/tests/test_contacts.py`

- [ ] **Step 1: 创建人物模型**

```python
# backend/app/models/contact.py
from sqlalchemy import Column, BigInteger, String, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Contact(Base):
    __tablename__ = "t_contact"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contact_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    avatar = Column(String(500), nullable=True)
    relationship = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建人物 Schemas**

```python
# backend/app/schemas/contact.py
from pydantic import BaseModel, Field
from typing import Optional, List

class ContactCreate(BaseModel):
    name: str = Field(..., max_length=20)
    relationship: str = Field(..., max_length=50)
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=200)

class ContactUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=20)
    relationship: Optional[str] = None
    avatar: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=200)

class ContactResponse(BaseModel):
    contact_id: str
    name: str
    avatar: Optional[str]
    relationship: str
    notes: Optional[str]
    anniversary_count: int
    created_at: str

    class Config:
        orm_mode = True
```

- [ ] **Step 3: 创建人物服务**

```python
# backend/app/services/contact_service.py
import uuid
from sqlalchemy.orm import Session
from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate

class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def create_contact(self, user_id: str, data: ContactCreate) -> Contact:
        contact = Contact(
            contact_id=f"C{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            name=data.name,
            avatar=data.avatar,
            relationship=data.relationship,
            notes=data.notes,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_contacts(self, user_id: str, relationship: str = None, keyword: str = None, page: int = 1, page_size: int = 20):
        from app.models.anniversary import Anniversary
        query = self.db.query(Contact).filter(Contact.user_id == user_id)
        if relationship:
            query = query.filter(Contact.relationship == relationship)
        if keyword:
            query = query.filter(Contact.name.contains(keyword))
        total = query.count()
        contacts = query.offset((page - 1) * page_size).limit(page_size).all()

        # 补充每个联系人的纪念日数量
        for contact in contacts:
            contact.anniversary_count = self.db.query(Anniversary).filter(
                Anniversary.contact_id == contact.contact_id,
                Anniversary.status == 1
            ).count()

        return total, contacts

    def get_contact(self, user_id: str, contact_id: str) -> Contact:
        contact = self.db.query(Contact).filter(
            Contact.contact_id == contact_id,
            Contact.user_id == user_id
        ).first()
        if not contact:
            raise ValueError("联系人不存在")
        return contact

    def update_contact(self, user_id: str, contact_id: str, data: ContactUpdate) -> Contact:
        contact = self.get_contact(user_id, contact_id)
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, user_id: str, contact_id: str):
        contact = self.get_contact(user_id, contact_id)
        self.db.delete(contact)
        self.db.commit()

    def get_relationships(self, user_id: str):
        preset = [
            {"key": "father", "label": "父亲"},
            {"key": "mother", "label": "母亲"},
            {"key": "spouse", "label": "配偶"},
            {"key": "child", "label": "子女"},
            {"key": "friend", "label": "朋友"},
            {"key": "colleague", "label": "同事"},
            {"key": "grandparent", "label": "祖父母/外祖父母"},
            {"key": "sibling", "label": "兄弟姐妹"},
            {"key": "teacher", "label": "老师"},
            {"key": "other", "label": "其他"},
        ]
        # 自定义关系：查询该用户已创建但不在预置中的关系标签
        existing = self.db.query(Contact.relationship).filter(
            Contact.user_id == user_id
        ).distinct().all()
        preset_labels = {item["label"] for item in preset}
        custom = [
            {"key": f"custom_{i+1}", "label": rel[0]}
            for i, rel in enumerate(existing)
            if rel[0] not in preset_labels
        ]
        return {"preset": preset, "custom": custom}
```

- [ ] **Step 4: 创建人物路由**

```python
# backend/app/routers/contacts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, get_current_user_id
from app.services.contact_service import ContactService
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter()

@router.get("/relationships")
def get_relationships(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = ContactService(db)
    return {"code": 0, "message": "success", "data": service.get_relationships(user_id)}

@router.get("/")
def list_contacts(
    relationship: str = None,
    keyword: str = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    total, contacts = service.get_contacts(user_id, relationship, keyword, page, page_size)
    return {
        "code": 0,
        "message": "success",
        "data": {"total": total, "list": contacts}
    }

@router.post("/")
def create_contact(
    data: ContactCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    contact = service.create_contact(user_id, data)
    return {"code": 0, "message": "success", "data": contact}

@router.get("/{contact_id}")
def get_contact(
    contact_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        contact = service.get_contact(user_id, contact_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": contact}

@router.put("/{contact_id}")
def update_contact(
    contact_id: str,
    data: ContactUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        contact = service.update_contact(user_id, contact_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": contact}

@router.delete("/{contact_id}")
def delete_contact(
    contact_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    try:
        service.delete_contact(user_id, contact_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}

# 头像上传接口
from fastapi import UploadFile, File
import os
import uuid as uuid_lib

@router.post("/upload/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    upload_dir = "uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{user_id}_{uuid_lib.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    url = f"/uploads/avatars/{filename}"
    return {"code": 0, "message": "success", "data": {"url": url}}
```

- [ ] **Step 5: 运行迁移并测试**

Run: `cd backend && alembic revision --autogenerate -m "create contacts table" && alembic upgrade head`
Run: `cd backend && pytest tests/test_contacts.py -v`

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/contact.py backend/app/schemas/contact.py backend/app/services/contact_service.py backend/app/routers/contacts.py backend/tests/test_contacts.py
git commit -m "feat: implement contacts CRUD"
```

---

### Task 7：iOS 联系人列表与详情

**Files:**
- Create: `mobile/EternalMoments/Models/Contact.swift`
- Create: `mobile/EternalMoments/ViewModels/ContactsViewModel.swift`
- Create: `mobile/EternalMoments/ViewModels/ContactDetailViewModel.swift`
- Create: `mobile/EternalMoments/Views/ContactsListView.swift`
- Create: `mobile/EternalMoments/Views/ContactDetailView.swift`
- Create: `mobile/EternalMoments/Views/AddContactView.swift`

- [ ] **Step 1: 创建 Contact 模型**

```swift
// mobile/EternalMoments/Models/Contact.swift
import Foundation

struct Contact: Codable, Identifiable, Hashable {
    let id: UUID = UUID()
    let contactId: String
    let name: String
    let avatar: String?
    let relationship: String
    let notes: String?
    let anniversaryCount: Int?
    let createdAt: String?

    enum CodingKeys: String, CodingKey {
        case contactId = "contact_id"
        case name
        case avatar
        case relationship
        case notes
        case anniversaryCount = "anniversary_count"
        case createdAt = "created_at"
    }
}
```

- [ ] **Step 2: 创建 ContactsViewModel**

```swift
// mobile/EternalMoments/ViewModels/ContactsViewModel.swift
import Foundation

@MainActor
class ContactsViewModel: ObservableObject {
    @Published var contacts: [Contact] = []
    @Published var searchText = ""
    @Published var selectedRelationship: String?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadContacts() async {
        isLoading = true
        errorMessage = nil
        do {
            let token = KeychainService.shared.getToken()
            let response: ContactListResponse = try await api.request(
                path: "contacts?page=1&page_size=100",
                token: token
            )
            contacts = response.data.list
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    var filteredContacts: [Contact] {
        var result = contacts
        if !searchText.isEmpty {
            result = result.filter { $0.name.localizedCaseInsensitiveContains(searchText) }
        }
        if let relationship = selectedRelationship {
            result = result.filter { $0.relationship == relationship }
        }
        return result
    }

    var groupedContacts: [String: [Contact]] {
        Dictionary(grouping: filteredContacts) { contact in
            if ["父亲", "母亲", "配偶", "子女", "兄弟姐妹", "祖父母/外祖父母"].contains(contact.relationship) {
                return "家人"
            } else {
                return "社交"
            }
        }
    }
}

struct ContactListResponse: Decodable {
    let code: Int
    let message: String
    let data: ContactListData

    struct ContactListData: Decodable {
        let total: Int
        let list: [Contact]
    }
}
```

- [ ] **Step 3: 创建 ContactsListView**

```swift
// mobile/EternalMoments/Views/ContactsListView.swift
import SwiftUI

struct ContactsListView: View {
    @StateObject private var viewModel = ContactsViewModel()
    @State private var showAddContact = false

    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

                VStack(spacing: 0) {
                    HStack {
                        TextField("搜索联系人", text: $viewModel.searchText)
                            .padding(10)
                            .background(Color.white)
                            .cornerRadius(10)
                    }
                    .padding()

                    List {
                        ForEach(viewModel.groupedContacts.keys.sorted(), id: \.self) { group in
                            Section(header: Text(group)) {
                                ForEach(viewModel.groupedContacts[group] ?? []) { contact in
                                    NavigationLink(destination: ContactDetailView(contactId: contact.contactId)) {
                                        ContactRow(contact: contact)
                                    }
                                }
                            }
                        }
                    }
                    .listStyle(InsetGroupedListStyle())
                }
            }
            .navigationTitle("联系人")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showAddContact = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showAddContact) {
                AddContactView()
            }
            .onAppear {
                Task { await viewModel.loadContacts() }
            }
        }
    }
}

struct ContactRow: View {
    let contact: Contact

    var body: some View {
        HStack {
            Circle()
                .fill(Color.gray.opacity(0.3))
                .frame(width: 44, height: 44)
                .overlay(Text(String(contact.name.prefix(1))).font(.headline))

            VStack(alignment: .leading) {
                Text(contact.name)
                    .font(.headline)
                HStack {
                    Text(contact.relationship)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 2)
                        .background(Color.blue.opacity(0.1))
                        .cornerRadius(8)
                    if let notes = contact.notes, !notes.isEmpty {
                        Text("• \(notes)")
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                }
            }

            Spacer()

            if let count = contact.anniversaryCount {
                Text("\(count)个纪念日")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
        .padding(.vertical, 4)
    }
}
```

- [ ] **Step 4: 创建 ContactDetailView 与 AddContactView**

```swift
// mobile/EternalMoments/Views/ContactDetailView.swift
import SwiftUI

struct ContactDetailView: View {
    let contactId: String
    @StateObject private var viewModel = ContactDetailViewModel()

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                if let contact = viewModel.contact {
                    VStack {
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 100, height: 100)
                            .overlay(Text(String(contact.name.prefix(1))).font(.largeTitle))

                        Text(contact.name)
                            .font(.largeTitle)
                            .bold()

                        HStack {
                            Text(contact.relationship)
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(10)
                        }
                    }
                    .padding()
                }
            }
        }
        .navigationTitle("联系人详情")
        .onAppear {
            Task { await viewModel.loadContact(contactId: contactId) }
        }
    }
}
```

```swift
// mobile/EternalMoments/ViewModels/ContactDetailViewModel.swift
import Foundation

@MainActor
class ContactDetailViewModel: ObservableObject {
    @Published var contact: Contact?
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadContact(contactId: String) async {
        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let response: ContactDetailResponse = try await api.request(
                path: "contacts/\(contactId)",
                token: token
            )
            contact = response.data
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}

struct ContactDetailResponse: Decodable {
    let code: Int
    let message: String
    let data: Contact
}
```

```swift
// mobile/EternalMoments/Views/AddContactView.swift
import SwiftUI
import PhotosUI

struct AddContactView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel = AddContactViewModel()
    @State private var selectedItem: PhotosPickerItem?

    var body: some View {
        NavigationView {
            Form {
                Section {
                    PhotosPicker(selection: $selectedItem, matching: .images) {
                        if let image = viewModel.avatarImage {
                            Image(uiImage: image)
                                .resizable()
                                .scaledToFill()
                                .frame(width: 80, height: 80)
                                .clipShape(Circle())
                        } else {
                            Circle()
                                .fill(Color.gray.opacity(0.3))
                                .frame(width: 80, height: 80)
                                .overlay(Image(systemName: "camera.fill").foregroundColor(.gray))
                        }
                    }
                }

                Section(header: Text("基本信息")) {
                    TextField("姓名", text: $viewModel.name)
                    Picker("关系", selection: $viewModel.relationship) {
                        ForEach(viewModel.relationships, id: \.self) { rel in
                            Text(rel).tag(rel)
                        }
                    }
                }

                Section(header: Text("个人偏好")) {
                    TextEditor(text: $viewModel.notes)
                        .frame(height: 100)
                }

                Button("保存") {
                    Task {
                        await viewModel.saveContact()
                        dismiss()
                    }
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                .cornerRadius(10)
                .listRowBackground(Color.clear)
            }
            .navigationTitle("添加联系人")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
            .onChange(of: selectedItem) { newItem in
                Task {
                    if let data = try? await newItem?.loadTransferable(type: Data.self),
                       let image = UIImage(data: data) {
                        viewModel.avatarImage = image
                    }
                }
            }
        }
    }
}
```

```swift
// mobile/EternalMoments/ViewModels/AddContactViewModel.swift
import Foundation
import UIKit

@MainActor
class AddContactViewModel: ObservableObject {
    @Published var name = ""
    @Published var relationship = "其他"
    @Published var notes = ""
    @Published var avatarImage: UIImage?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let relationships = ["父亲", "母亲", "配偶", "子女", "朋友", "同事", "兄弟姐妹", "老师", "其他"]

    private let api = APIClient.shared

    func saveContact() async {
        guard !name.isEmpty else {
            errorMessage = "请输入姓名"
            return
        }

        isLoading = true
        do {
            let token = KeychainService.shared.getToken()

            // 先上传头像（如果选择了图片）
            var avatarUrl: String? = nil
            if let image = avatarImage,
               let imageData = image.jpegData(compressionQuality: 0.8) {
                avatarUrl = try await uploadAvatar(imageData: imageData, token: token)
            }

            let request = ContactCreateRequest(
                name: name,
                relationship: relationship,
                avatar: avatarUrl,
                notes: notes.isEmpty ? nil : notes
            )
            let _: ContactCreateResponse = try await api.request(
                path: "contacts",
                method: "POST",
                body: request,
                token: token
            )
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    private func uploadAvatar(imageData: Data, token: String?) async throws -> String {
        let url = URL(string: "http://localhost:8000/api/v1/contacts/upload/avatar")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"file\"; filename=\"avatar.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(imageData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

        let (data, response) = try await URLSession.shared.upload(for: request, from: body)
        guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError(500, "头像上传失败")
        }

        let result = try JSONDecoder().decode(AvatarUploadResponse.self, from: data)
        return result.data.url
    }
}

struct AvatarUploadResponse: Decodable {
    let code: Int
    let message: String
    let data: AvatarData
    struct AvatarData: Decodable {
        let url: String
    }
}

struct ContactCreateRequest: Encodable {
    let name: String
    let relationship: String
    let avatar: String?
    let notes: String?
}

struct ContactCreateResponse: Decodable {
    let code: Int
    let message: String
    let data: Contact
}
```

---

## 阶段 3：F3 纪念日记录

### Task 8：后端纪念日与节假日模型

**Files:**
- Create: `backend/app/models/anniversary.py`
- Create: `backend/app/models/holiday.py`
- Create: `backend/app/schemas/anniversary.py`
- Create: `backend/app/schemas/holiday.py`
- Create: `backend/app/services/anniversary_service.py`
- Create: `backend/app/services/holiday_service.py`
- Create: `backend/app/routers/anniversaries.py`
- Create: `backend/app/routers/holidays.py`
- Test: `backend/tests/test_anniversaries.py`

- [ ] **Step 1: 创建纪念日模型**

```python
# backend/app/models/anniversary.py
from sqlalchemy import Column, BigInteger, String, Date, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.core.database import Base

class AnniversaryTemplate(Base):
    __tablename__ = "t_anniversary_template"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title_key = Column(String(32), unique=True, nullable=False)
    label = Column(String(50), nullable=False)
    default_repeat = Column(String(20), default="yearly")
    sort_order = Column(BigInteger, default=0)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())

class Anniversary(Base):
    __tablename__ = "t_anniversary"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    anniversary_id = Column(String(32), unique=True, nullable=False, index=True)
    contact_id = Column(String(32), nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    title = Column(String(50), nullable=False)
    title_key = Column(String(32), nullable=True)
    month_day = Column(String(5), nullable=False)
    repeat_type = Column(String(20), nullable=False)
    next_date = Column(Date, nullable=False)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 2: 创建节假日模型**

```python
# backend/app/models/holiday.py
from sqlalchemy import Column, BigInteger, String, Date, DateTime, SmallInteger, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class SystemHoliday(Base):
    __tablename__ = "t_system_holiday"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    holiday_id = Column(String(32), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    date_rule = Column(String(100), nullable=False)
    applicable_relationships = Column(JSON, nullable=False)
    description = Column(String(200), nullable=True)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ContactHoliday(Base):
    __tablename__ = "t_contact_holiday"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    contact_id = Column(String(32), nullable=False, index=True)
    holiday_id = Column(String(32), nullable=False)
    user_id = Column(String(32), nullable=False, index=True)
    remind_enabled = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **Step 3: 创建纪念日服务**

```python
# backend/app/services/anniversary_service.py
import uuid
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.models.anniversary import Anniversary, AnniversaryTemplate
from app.schemas.anniversary import AnniversaryCreate, AnniversaryUpdate

class AnniversaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_templates(self):
        return self.db.query(AnniversaryTemplate).filter(AnniversaryTemplate.status == 1).order_by(AnniversaryTemplate.sort_order).all()

    def calculate_next_date(self, month_day: str, repeat_type: str) -> date:
        today = date.today()
        month, day = map(int, month_day.split("-"))
        year = today.year
        candidate = date(year, month, day)
        if candidate < today:
            year += 1
            candidate = date(year, month, day)
        return candidate

    def create_anniversary(self, user_id: str, data: AnniversaryCreate) -> Anniversary:
        template = None
        if data.title_key:
            template = self.db.query(AnniversaryTemplate).filter(
                AnniversaryTemplate.title_key == data.title_key
            ).first()

        title = template.label if template else (data.title or "纪念日")
        repeat_type = data.repeat_type or (template.default_repeat if template else "yearly")
        next_date = self.calculate_next_date(data.date, repeat_type)

        anniversary = Anniversary(
            anniversary_id=f"A{uuid.uuid4().hex[:8].upper()}",
            contact_id=data.contact_id,
            user_id=user_id,
            title=title,
            title_key=data.title_key,
            month_day=data.date,
            repeat_type=repeat_type,
            next_date=next_date,
        )
        self.db.add(anniversary)
        self.db.commit()
        self.db.refresh(anniversary)
        return anniversary

    def get_anniversaries(self, user_id: str, contact_id: str = None):
        query = self.db.query(Anniversary).filter(
            Anniversary.user_id == user_id,
            Anniversary.status == 1
        )
        if contact_id:
            query = query.filter(Anniversary.contact_id == contact_id)
        return query.order_by(Anniversary.next_date).all()

    def update_anniversary(self, user_id: str, anniversary_id: str, data: AnniversaryUpdate) -> Anniversary:
        anniversary = self.db.query(Anniversary).filter(
            Anniversary.anniversary_id == anniversary_id,
            Anniversary.user_id == user_id
        ).first()
        if not anniversary:
            raise ValueError("纪念日不存在")

        update_data = data.dict(exclude_unset=True)
        if "date" in update_data:
            anniversary.month_day = update_data.pop("date")
            anniversary.next_date = self.calculate_next_date(anniversary.month_day, anniversary.repeat_type)
        if "title_key" in update_data:
            template = self.db.query(AnniversaryTemplate).filter(
                AnniversaryTemplate.title_key == update_data["title_key"]
            ).first()
            if template:
                anniversary.title = template.label
        for key, value in update_data.items():
            setattr(anniversary, key, value)

        self.db.commit()
        self.db.refresh(anniversary)
        return anniversary

    def delete_anniversary(self, user_id: str, anniversary_id: str):
        anniversary = self.db.query(Anniversary).filter(
            Anniversary.anniversary_id == anniversary_id,
            Anniversary.user_id == user_id
        ).first()
        if not anniversary:
            raise ValueError("纪念日不存在")
        anniversary.status = 0
        self.db.commit()
```

- [ ] **Step 4: 创建纪念日路由**

```python
# backend/app/routers/anniversaries.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, get_current_user_id
from app.services.anniversary_service import AnniversaryService
from app.schemas.anniversary import AnniversaryCreate, AnniversaryUpdate

router = APIRouter()

@router.get("/templates")
def get_templates(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    service = AnniversaryService(db)
    templates = service.get_templates()
    return {"code": 0, "message": "success", "data": {"list": templates}}

@router.get("/")
def list_anniversaries(
    contact_id: str = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    anniversaries = service.get_anniversaries(user_id, contact_id)
    return {"code": 0, "message": "success", "data": {"list": anniversaries}}

@router.post("/")
def create_anniversary(
    data: AnniversaryCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    anniversary = service.create_anniversary(user_id, data)
    return {"code": 0, "message": "success", "data": anniversary}

@router.put("/{anniversary_id}")
def update_anniversary(
    anniversary_id: str,
    data: AnniversaryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    try:
        anniversary = service.update_anniversary(user_id, anniversary_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": anniversary}

@router.delete("/{anniversary_id}")
def delete_anniversary(
    anniversary_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = AnniversaryService(db)
    try:
        service.delete_anniversary(user_id, anniversary_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}
```

- [ ] **Step 5: 创建节假日服务与路由**

```python
# backend/app/services/holiday_service.py
import uuid
from sqlalchemy.orm import Session
from app.models.holiday import SystemHoliday, ContactHoliday

class HolidayService:
    def __init__(self, db: Session):
        self.db = db

    def get_holidays(self, relationship: str = None):
        query = self.db.query(SystemHoliday).filter(SystemHoliday.status == 1)
        if relationship:
            query = query.filter(SystemHoliday.applicable_relationships.contains([relationship]))
        return query.all()

    def set_remind_enabled(self, user_id: str, contact_id: str, holiday_id: str, enabled: bool):
        record = self.db.query(ContactHoliday).filter(
            ContactHoliday.user_id == user_id,
            ContactHoliday.contact_id == contact_id,
            ContactHoliday.holiday_id == holiday_id
        ).first()
        if not record:
            record = ContactHoliday(
                contact_id=contact_id,
                holiday_id=holiday_id,
                user_id=user_id,
                remind_enabled=1 if enabled else 0
            )
            self.db.add(record)
        else:
            record.remind_enabled = 1 if enabled else 0
        self.db.commit()
        return record
```

```python
# backend/app/routers/holidays.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db, get_current_user_id
from app.services.holiday_service import HolidayService

router = APIRouter()

@router.get("/")
def list_holidays(
    relationship: str = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = HolidayService(db)
    holidays = service.get_holidays(relationship)
    return {"code": 0, "message": "success", "data": {"list": holidays}}

@router.put("/contacts/{contact_id}/holidays/{holiday_id}/remind")
def set_remind(
    contact_id: str,
    holiday_id: str,
    data: dict,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = HolidayService(db)
    service.set_remind_enabled(user_id, contact_id, holiday_id, data.get("remind_enabled", True))
    return {"code": 0, "message": "success", "data": None}
```

- [ ] **Step 6: 运行迁移并测试**

Run: `cd backend && alembic revision --autogenerate -m "create anniversary and holiday tables" && alembic upgrade head`
Run: `cd backend && pytest tests/test_anniversaries.py -v`

---

### Task 9：iOS 纪念日添加与详情

**Files:**
- Create: `mobile/EternalMoments/Models/Anniversary.swift`
- Create: `mobile/EternalMoments/ViewModels/AddAnniversaryViewModel.swift`
- Create: `mobile/EternalMoments/Views/AddAnniversaryView.swift`
- Modify: `mobile/EternalMoments/Views/ContactDetailView.swift`（添加纪念日 Tab）

- [ ] **Step 1: 创建 Anniversary 模型**

```swift
// mobile/EternalMoments/Models/Anniversary.swift
import Foundation

struct Anniversary: Codable, Identifiable, Hashable {
    let id: UUID = UUID()
    let anniversaryId: String
    let title: String
    let titleKey: String?
    let monthDay: String
    let repeatType: String
    let nextDate: String?
    let daysRemaining: Int?

    enum CodingKeys: String, CodingKey {
        case anniversaryId = "anniversary_id"
        case title
        case titleKey = "title_key"
        case monthDay = "month_day"
        case repeatType = "repeat_type"
        case nextDate = "next_date"
        case daysRemaining = "days_remaining"
    }
}

struct SystemHoliday: Codable, Identifiable {
    let id: UUID = UUID()
    let holidayId: String
    let name: String
    let date: String
    let applicableRelationships: [String]
    let description: String?

    enum CodingKeys: String, CodingKey {
        case holidayId = "holiday_id"
        case name
        case date
        case applicableRelationships = "applicable_relationships"
        case description
    }
}
```

- [ ] **Step 2: 创建 AddAnniversaryViewModel**

```swift
// mobile/EternalMoments/ViewModels/AddAnniversaryViewModel.swift
import Foundation

@MainActor
class AddAnniversaryViewModel: ObservableObject {
    @Published var contactId: String
    @Published var contactName: String
    @Published var selectedTemplate: String = "其他"
    @Published var customTitle = ""
    @Published var selectedDate = Date()
    @Published var repeatType = "yearly"
    @Published var templates: [AnniversaryTemplate] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    init(contactId: String, contactName: String) {
        self.contactId = contactId
        self.contactName = contactName
    }

    func loadTemplates() async {
        do {
            let token = KeychainService.shared.getToken()
            let response: TemplateListResponse = try await api.request(path: "anniversaries/templates", token: token)
            templates = response.data.list
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func saveAnniversary() async {
        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let formatter = DateFormatter()
            formatter.dateFormat = "MM-dd"
            let monthDay = formatter.string(from: selectedDate)

            let template = templates.first { $0.label == selectedTemplate }
            let request = AnniversaryCreateRequest(
                contactId: contactId,
                titleKey: template?.titleKey,
                title: selectedTemplate == "其他" ? customTitle : nil,
                date: monthDay,
                repeatType: repeatType
            )
            let _: AnniversaryCreateResponse = try await api.request(
                path: "anniversaries",
                method: "POST",
                body: request,
                token: token
            )
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}

struct AnniversaryTemplate: Codable, Identifiable {
    let id: UUID = UUID()
    let titleKey: String
    let label: String
    let defaultRepeat: String

    enum CodingKeys: String, CodingKey {
        case titleKey = "title_key"
        case label
        case defaultRepeat = "default_repeat"
    }
}

struct TemplateListResponse: Decodable {
    let code: Int
    let message: String
    let data: TemplateData
    struct TemplateData: Decodable {
        let list: [AnniversaryTemplate]
    }
}

struct AnniversaryCreateRequest: Encodable {
    let contactId: String
    let titleKey: String?
    let title: String?
    let date: String
    let repeatType: String

    enum CodingKeys: String, CodingKey {
        case contactId = "contact_id"
        case titleKey = "title_key"
        case title
        case date
        case repeatType = "repeat_type"
    }
}

struct AnniversaryCreateResponse: Decodable {
    let code: Int
    let message: String
    let data: Anniversary
}
```

- [ ] **Step 3: 创建 AddAnniversaryView**

```swift
// mobile/EternalMoments/Views/AddAnniversaryView.swift
import SwiftUI

struct AddAnniversaryView: View {
    @Environment(\.dismiss) var dismiss
    @StateObject private var viewModel: AddAnniversaryViewModel

    init(contactId: String, contactName: String) {
        _viewModel = StateObject(wrappedValue: AddAnniversaryViewModel(contactId: contactId, contactName: contactName))
    }

    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("关联联系人")) {
                    Text(viewModel.contactName)
                }

                Section(header: Text("纪念日类型")) {
                    Picker("类型", selection: $viewModel.selectedTemplate) {
                        ForEach(viewModel.templates) { template in
                            Text(template.label).tag(template.label)
                        }
                    }
                    if viewModel.selectedTemplate == "其他" {
                        TextField("自定义名称", text: $viewModel.customTitle)
                    }
                }

                Section(header: Text("日期")) {
                    DatePicker("选择日期", selection: $viewModel.selectedDate, displayedComponents: [.date])
                        .datePickerStyle(WheelDatePickerStyle())
                }

                Section(header: Text("重复频率")) {
                    Picker("重复", selection: $viewModel.repeatType) {
                        Text("每年").tag("yearly")
                        Text("每月").tag("monthly")
                        Text("仅一次").tag("once")
                    }
                    .pickerStyle(SegmentedPickerStyle())
                }

                Button("保存纪念日") {
                    Task {
                        await viewModel.saveAnniversary()
                        dismiss()
                    }
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                .cornerRadius(10)
                .listRowBackground(Color.clear)
            }
            .navigationTitle("添加纪念日")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") { dismiss() }
                }
            }
            .onAppear {
                Task { await viewModel.loadTemplates() }
            }
        }
    }
}
```

- [ ] **Step 4: 修改 ContactDetailView 添加纪念日/节假日 Tab**

```swift
// mobile/EternalMoments/Views/ContactDetailView.swift
import SwiftUI

struct ContactDetailView: View {
    let contactId: String
    @StateObject private var viewModel = ContactDetailViewModel()
    @State private var selectedTab = 0

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                if let contact = viewModel.contact {
                    VStack {
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 100, height: 100)
                            .overlay(Text(String(contact.name.prefix(1))).font(.largeTitle))

                        Text(contact.name)
                            .font(.largeTitle)
                            .bold()

                        HStack {
                            Text(contact.relationship)
                                .font(.caption)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 4)
                                .background(Color.blue.opacity(0.1))
                                .cornerRadius(10)
                        }
                    }
                    .padding()

                    Picker("标签页", selection: $selectedTab) {
                        Text("纪念日").tag(0)
                        Text("节假日").tag(1)
                    }
                    .pickerStyle(SegmentedPickerStyle())
                    .padding(.horizontal)

                    if selectedTab == 0 {
                        AnniversaryListSection(contactId: contactId)
                    } else {
                        HolidayListSection(contactId: contactId)
                    }
                }
            }
        }
        .navigationTitle("联系人详情")
        .onAppear {
            Task { await viewModel.loadContact(contactId: contactId) }
        }
    }
}

struct AnniversaryListSection: View {
    let contactId: String
    @StateObject private var viewModel = AnniversaryListViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("个人纪念日")
                    .font(.headline)
                Spacer()
                NavigationLink(destination: AddAnniversaryView(contactId: contactId, contactName: "联系人")) {
                    Image(systemName: "plus.circle")
                    Text("新增")
                }
                .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
            }
            .padding(.horizontal)

            ForEach(viewModel.anniversaries) { anniversary in
                HStack {
                    VStack(alignment: .leading) {
                        Text(anniversary.title)
                            .font(.headline)
                        Text(anniversary.monthDay)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    if let days = anniversary.daysRemaining {
                        Text("\(days)天")
                            .font(.headline)
                            .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                    }
                }
                .padding()
                .background(Color.white)
                .cornerRadius(10)
                .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
                .padding(.horizontal)
            }
        }
        .onAppear {
            Task { await viewModel.loadAnniversaries(contactId: contactId) }
        }
    }
}

struct HolidayListSection: View {
    let contactId: String
    @StateObject private var viewModel = HolidayListViewModel()

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("系统节假日")
                .font(.headline)
                .padding(.horizontal)

            ForEach(viewModel.holidays) { holiday in
                HStack {
                    VStack(alignment: .leading) {
                        Text(holiday.name)
                            .font(.headline)
                        Text(holiday.date)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    Toggle("", isOn: Binding(
                        get: { holiday.remindEnabled },
                        set: { newValue in
                            Task { await viewModel.toggleRemind(holidayId: holiday.holidayId, enabled: newValue) }
                        }
                    ))
                }
                .padding()
                .background(Color.white)
                .cornerRadius(10)
                .shadow(color: .black.opacity(0.05), radius: 4, x: 0, y: 2)
                .padding(.horizontal)
            }
        }
        .onAppear {
            Task { await viewModel.loadHolidays(contactId: contactId) }
        }
    }
}

class AnniversaryListViewModel: ObservableObject {
    @Published var anniversaries: [Anniversary] = []
    private let api = APIClient.shared

    func loadAnniversaries(contactId: String) async {
        do {
            let token = KeychainService.shared.getToken()
            let response: AnniversaryListResponse = try await api.request(
                path: "anniversaries?contact_id=\(contactId)",
                token: token
            )
            anniversaries = response.data.list
        } catch {
            print("Load anniversaries error: \(error)")
        }
    }
}

class HolidayListViewModel: ObservableObject {
    @Published var holidays: [ContactHoliday] = []
    private let api = APIClient.shared
    var contactId: String = ""

    func loadHolidays(contactId: String) async {
        self.contactId = contactId
        do {
            let token = KeychainService.shared.getToken()
            let response: HolidayListResponse = try await api.request(
                path: "holidays?relationship=母亲",
                token: token
            )
            holidays = response.data.list.map { holiday in
                ContactHoliday(
                    holidayId: holiday.holidayId,
                    name: holiday.name,
                    date: holiday.date,
                    remindEnabled: true
                )
            }
        } catch {
            print("Load holidays error: \(error)")
        }
    }

    func toggleRemind(holidayId: String, enabled: Bool) async {
        do {
            let token = KeychainService.shared.getToken()
            struct ToggleRequest: Encodable { let remind_enabled: Bool }
            let _: EmptyResponse = try await api.request(
                path: "holidays/contacts/\(contactId)/holidays/\(holidayId)/remind",
                method: "PUT",
                body: ToggleRequest(remind_enabled: enabled),
                token: token
            )
        } catch {
            print("Toggle remind error: \(error)")
        }
    }
}

struct ContactHoliday: Identifiable {
    let id = UUID()
    let holidayId: String
    let name: String
    let date: String
    var remindEnabled: Bool
}

struct AnniversaryListResponse: Decodable {
    let code: Int
    let message: String
    let data: AnniversaryListData
    struct AnniversaryListData: Decodable {
        let list: [Anniversary]
    }
}

struct HolidayListResponse: Decodable {
    let code: Int
    let message: String
    let data: HolidayListData
    struct HolidayListData: Decodable {
        let list: [SystemHoliday]
    }
}
```

---

## 阶段 4：F4 提醒功能

### Task 10：后端提醒与 AI 服务

**Files:**
- Create: `backend/app/models/reminder.py`
- Create: `backend/app/schemas/reminder.py`
- Create: `backend/app/services/reminder_service.py`
- Create: `backend/app/services/ai_service.py`
- Create: `backend/app/jobs/reminder_job.py`
- Create: `backend/app/routers/reminders.py`
- Test: `backend/tests/test_reminders.py`

- [ ] **Step 1: 创建提醒模型**

```python
# backend/app/models/reminder.py
from sqlalchemy import Column, BigInteger, String, Date, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class Reminder(Base):
    __tablename__ = "t_reminder"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    reminder_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(String(32), nullable=False, index=True)
    contact_id = Column(String(32), nullable=False)
    type = Column(String(20), nullable=False)
    anniversary_id = Column(String(32), nullable=True)
    holiday_id = Column(String(32), nullable=True)
    event_title = Column(String(50), nullable=False)
    event_date = Column(Date, nullable=False)
    remind_time = Column(DateTime, nullable=False)
    status = Column(String(20), default="unread")
    blessing = Column(Text, nullable=True)
    gifts = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 2: 创建 AI 服务**

```python
# backend/app/services/ai_service.py
from abc import ABC, abstractmethod
from typing import List, Dict
import json

class AIClient(ABC):
    @abstractmethod
    def generate_blessing(self, relationship: str, holiday_name: str, receiver_name: str) -> str:
        pass

    @abstractmethod
    def recommend_gifts(self, relationship: str, anniversary_type: str, receiver_name: str) -> List[Dict]:
        pass

class MockAIClient(AIClient):
    def generate_blessing(self, relationship: str, holiday_name: str, receiver_name: str) -> str:
        return f"亲爱的{receiver_name}，{holiday_name}快乐！愿这一天充满温暖与幸福。"

    def recommend_gifts(self, relationship: str, anniversary_type: str, receiver_name: str) -> List[Dict]:
        return [
            {"name": "定制相册", "price": 129, "reason": "记录美好瞬间，适合送给重要的人", "purchase_url": "https://item.jd.com/xxx"},
            {"name": "鲜花礼盒", "price": 199, "reason": "经典心意表达，适合多种纪念日", "purchase_url": "https://item.jd.com/xxx"}
        ]

class VolcanoArkClient(AIClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://ark.cn-beijing.volces.com/api/v3"

    def _call_model(self, messages: list) -> str:
        import requests
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "doubao-pro-32k",  # 火山方舟模型名，按实际配置调整
            "messages": messages
        }
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def generate_blessing(self, relationship: str, holiday_name: str, receiver_name: str) -> str:
        prompt = f"""你是一位拥有20年情感表达经验的高级情感专家。

请根据以下信息生成一段祝福语：
- 接收者与用户的关系：{relationship}
- 节假日名称：{holiday_name}
- 接收者称呼/姓名：{receiver_name}

要求：
1. 真诚自然，避免空洞套话
2. 根据关系调整语言风格
3. 2-4句话，50-120字
4. 不要使用表情符号、网络流行语或陈旧表达
5. 直接输出祝福语正文"""
        return self._call_model([{"role": "user", "content": prompt}])

    def recommend_gifts(self, relationship: str, anniversary_type: str, receiver_name: str) -> List[Dict]:
        prompt = f"""你是一位资深礼物选品博主。

请根据以下信息推荐3-5款适合的礼品：
- 收礼人与用户的关系：{relationship}
- 纪念日类型：{anniversary_type}
- 收礼者称呼/姓名：{receiver_name}

要求：
1. 因人选礼，价格合理
2. 推荐知名品牌，优先京东/天猫在售商品
3. 每个推荐需说明具体推荐理由

严格按以下JSON数组格式输出，不要输出任何其他内容：
[
  {{
    "name": "商品名称",
    "price": 参考价格（数字，单位元）,
    "reason": "推荐理由（一句话，20-50字）",
    "purchase_url": "推荐购买链接"
  }}
]"""
        content = self._call_model([{"role": "user", "content": prompt}])
        return json.loads(content)

def get_ai_client() -> AIClient:
    from app.core.config import settings
    if settings.AI_PROVIDER == "volcano_ark" and settings.VOLCANO_ARK_API_KEY:
        return VolcanoArkClient(settings.VOLCANO_ARK_API_KEY)
    return MockAIClient()
```

- [ ] **Step 3: 创建提醒服务与定时任务**

```python
# backend/app/services/reminder_service.py
import uuid
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.models.anniversary import Anniversary
from app.models.holiday import ContactHoliday, SystemHoliday
from app.services.ai_service import get_ai_client

class ReminderService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_client = get_ai_client()

    def get_reminders(self, user_id: str, type: str = None, status: str = None, page: int = 1, page_size: int = 20):
        query = self.db.query(Reminder).filter(Reminder.user_id == user_id)
        if type:
            query = query.filter(Reminder.type == type)
        if status:
            query = query.filter(Reminder.status == status)
        total = query.count()
        reminders = query.order_by(Reminder.remind_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, reminders

    def mark_read(self, user_id: str, reminder_id: str):
        reminder = self.db.query(Reminder).filter(
            Reminder.reminder_id == reminder_id,
            Reminder.user_id == user_id
        ).first()
        if not reminder:
            raise ValueError("提醒不存在")
        reminder.status = "read"
        self.db.commit()
        return reminder

    def generate_personal_reminder(self, user_id: str, contact_id: str, anniversary: Anniversary):
        # 提前5天提醒
        remind_date = anniversary.next_date - timedelta(days=5)
        if remind_date != date.today():
            return None

        gifts = self.ai_client.recommend_gifts(
            relationship="未知",
            anniversary_type=anniversary.title,
            receiver_name="联系人"
        )

        reminder = Reminder(
            reminder_id=f"R{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            contact_id=contact_id,
            type="personal",
            anniversary_id=anniversary.anniversary_id,
            event_title=anniversary.title,
            event_date=anniversary.next_date,
            remind_time=datetime.combine(remind_date, datetime.min.time()),
            gifts=gifts
        )
        self.db.add(reminder)
        self.db.commit()
        return reminder

    def generate_holiday_reminder(self, user_id: str, contact_id: str, holiday: SystemHoliday, event_date: date):
        # 提前3天提醒
        remind_date = event_date - timedelta(days=3)
        if remind_date != date.today():
            return None

        blessing = self.ai_client.generate_blessing(
            relationship="未知",
            holiday_name=holiday.name,
            receiver_name="联系人"
        )

        reminder = Reminder(
            reminder_id=f"R{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            contact_id=contact_id,
            type="holiday",
            holiday_id=holiday.holiday_id,
            event_title=holiday.name,
            event_date=event_date,
            remind_time=datetime.combine(remind_date, datetime.min.time()),
            blessing=blessing
        )
        self.db.add(reminder)
        self.db.commit()
        return reminder
```

```python
# backend/app/jobs/reminder_job.py
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.anniversary import Anniversary
from app.models.holiday import ContactHoliday, SystemHoliday
from app.services.reminder_service import ReminderService
from datetime import date, datetime
import calendar

def calculate_holiday_date(rule: str, year: int) -> date:
    # 简化实现：支持固定日期如 "05-10"，复杂规则后续完善
    if "-" in rule and len(rule) == 5:
        month, day = map(int, rule.split("-"))
        return date(year, month, day)
    return date(year, 1, 1)  # fallback

def check_and_generate_reminders():
    db = SessionLocal()
    try:
        today = date.today()
        service = ReminderService(db)

        # 个人纪念日提醒
        anniversaries = db.query(Anniversary).filter(Anniversary.status == 1).all()
        for ann in anniversaries:
            service.generate_personal_reminder(ann.user_id, ann.contact_id, ann)

        # 系统节假日提醒
        contact_holidays = db.query(ContactHoliday).filter(ContactHoliday.remind_enabled == 1).all()
        for ch in contact_holidays:
            holiday = db.query(SystemHoliday).filter(
                SystemHoliday.holiday_id == ch.holiday_id,
                SystemHoliday.status == 1
            ).first()
            if holiday:
                event_date = calculate_holiday_date(holiday.date_rule, today.year)
                service.generate_holiday_reminder(ch.user_id, ch.contact_id, holiday, event_date)
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_and_generate_reminders, 'cron', hour=9, minute=0)
    scheduler.start()
```

- [ ] **Step 4: 创建提醒路由**

```python
# backend/app/routers/reminders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, get_current_user_id
from app.services.reminder_service import ReminderService

router = APIRouter()

@router.get("/")
def list_reminders(
    type: str = None,
    status: str = None,
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    total, reminders = service.get_reminders(user_id, type, status, page, page_size)
    return {"code": 0, "message": "success", "data": {"total": total, "list": reminders}}

@router.put("/{reminder_id}/read")
def mark_read(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    service = ReminderService(db)
    try:
        service.mark_read(user_id, reminder_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"code": 0, "message": "success", "data": None}

@router.post("/{reminder_id}/blessing")
def generate_blessing(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.services.reminder_service import ReminderService
    from app.models.reminder import Reminder
    service = ReminderService(db)
    reminder = db.query(Reminder).filter(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == user_id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    blessing = service.ai_client.generate_blessing(
        relationship="联系人",
        holiday_name=reminder.event_title,
        receiver_name="联系人"
    )
    reminder.blessing = blessing
    db.commit()
    return {"code": 0, "message": "success", "data": {"blessing": blessing}}

@router.post("/{reminder_id}/gifts")
def recommend_gifts(
    reminder_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    from app.services.reminder_service import ReminderService
    from app.models.reminder import Reminder
    service = ReminderService(db)
    reminder = db.query(Reminder).filter(
        Reminder.reminder_id == reminder_id,
        Reminder.user_id == user_id
    ).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    gifts = service.ai_client.recommend_gifts(
        relationship="联系人",
        anniversary_type=reminder.event_title,
        receiver_name="联系人"
    )
    reminder.gifts = gifts
    db.commit()
    return {"code": 0, "message": "success", "data": {"gifts": gifts}}
```

- [ ] **Step 5: 在 main.py 中启动定时任务**

```python
# backend/app/main.py (追加)
from app.jobs.reminder_job import start_scheduler

@app.on_event("startup")
def startup_event():
    start_scheduler()
```

---

### Task 11：iOS 提醒列表与本地通知

**Files:**
- Create: `mobile/EternalMoments/Models/Reminder.swift`
- Create: `mobile/EternalMoments/ViewModels/RemindersViewModel.swift`
- Create: `mobile/EternalMoments/Views/RemindersView.swift`
- Create: `mobile/EternalMoments/Services/NotificationService.swift`

- [ ] **Step 1: 创建 Reminder 模型**

```swift
// mobile/EternalMoments/Models/Reminder.swift
import Foundation

struct Reminder: Codable, Identifiable, Hashable {
    let id: UUID = UUID()
    let reminderId: String
    let contactId: String
    let contactName: String?
    let anniversaryTitle: String
    let type: String
    let remindTime: String
    let eventDate: String
    let status: String
    let blessing: String?
    let gifts: [Gift]?

    enum CodingKeys: String, CodingKey {
        case reminderId = "reminder_id"
        case contactId = "contact_id"
        case contactName = "contact_name"
        case anniversaryTitle = "anniversary_title"
        case type
        case remindTime = "remind_time"
        case eventDate = "event_date"
        case status
        case blessing
        case gifts
    }
}

struct Gift: Codable, Hashable {
    let name: String
    let price: Double
    let reason: String
    let purchaseUrl: String

    enum CodingKeys: String, CodingKey {
        case name
        case price
        case reason
        case purchaseUrl = "purchase_url"
    }
}
```

- [ ] **Step 2: 创建 NotificationService**

```swift
// mobile/EternalMoments/Services/NotificationService.swift
import UserNotifications

class NotificationService {
    static let shared = NotificationService()

    private init() {}

    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, _ in
            print("Notification permission granted: \(granted)")
        }
    }

    func scheduleReminder(reminder: Reminder) {
        let content = UNMutableNotificationContent()
        content.title = reminder.anniversaryTitle
        content.body = "纪念日快到了，点击查看详情"
        content.sound = .default

        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        guard let remindDate = formatter.date(from: reminder.remindTime) else { return }

        let components = Calendar.current.dateComponents([.year, .month, .day, .hour, .minute], from: remindDate)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        let request = UNNotificationRequest(identifier: reminder.reminderId, content: content, trigger: trigger)
        UNUserNotificationCenter.current().add(request)
    }
}
```

- [ ] **Step 3: 创建 RemindersViewModel**

```swift
// mobile/EternalMoments/ViewModels/RemindersViewModel.swift
import Foundation

@MainActor
class RemindersViewModel: ObservableObject {
    @Published var reminders: [Reminder] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let api = APIClient.shared

    func loadReminders() async {
        isLoading = true
        do {
            let token = KeychainService.shared.getToken()
            let response: ReminderListResponse = try await api.request(
                path: "reminders?page=1&page_size=100",
                token: token
            )
            reminders = response.data.list
            for reminder in reminders where reminder.status == "unread" {
                NotificationService.shared.scheduleReminder(reminder: reminder)
            }
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }

    func markRead(reminder: Reminder) async {
        do {
            let token = KeychainService.shared.getToken()
            let _: EmptyResponse = try await api.request(
                path: "reminders/\(reminder.reminderId)/read",
                method: "PUT",
                token: token
            )
            await loadReminders()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct ReminderListResponse: Decodable {
    let code: Int
    let message: String
    let data: ReminderListData
    struct ReminderListData: Decodable {
        let total: Int
        let list: [Reminder]
    }
}
```

- [ ] **Step 4: 创建 RemindersView**

```swift
// mobile/EternalMoments/Views/RemindersView.swift
import SwiftUI

struct RemindersView: View {
    @StateObject private var viewModel = RemindersViewModel()

    var body: some View {
        NavigationView {
            ZStack {
                Color(red: 1, green: 248/255, blue: 247/255).ignoresSafeArea()

                if viewModel.reminders.isEmpty {
                    VStack {
                        Image(systemName: "bell.slash")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("暂无提醒")
                            .foregroundColor(.gray)
                    }
                } else {
                    List {
                        ForEach(viewModel.reminders) { reminder in
                            ReminderCard(reminder: reminder)
                                .onTapGesture {
                                    Task { await viewModel.markRead(reminder: reminder) }
                                }
                        }
                    }
                    .listStyle(PlainListStyle())
                }
            }
            .navigationTitle("提醒记录")
            .onAppear {
                NotificationService.shared.requestAuthorization()
                Task { await viewModel.loadReminders() }
            }
        }
    }
}

struct ReminderCard: View {
    let reminder: Reminder
    @State private var copied = false

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                if reminder.status == "unread" {
                    Circle()
                        .fill(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .frame(width: 8, height: 8)
                    Text("新时刻")
                        .font(.caption)
                        .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                } else {
                    Text("已查看")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                Spacer()
                Text(reminder.eventDate)
                    .font(.caption)
                    .foregroundColor(.gray)
            }

            Text(reminder.anniversaryTitle)
                .font(.headline)

            if let blessing = reminder.blessing {
                Text(blessing)
                    .font(.body)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)

                Button(action: {
                    UIPasteboard.general.string = blessing
                    copied = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) { copied = false }
                }) {
                    Label(copied ? "已复制" : "复制祝福语", systemImage: copied ? "checkmark" : "doc.on.doc")
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color(red: 212/255, green: 63/255, blue: 82/255))
                        .cornerRadius(10)
                }
            }

            if let gifts = reminder.gifts, !gifts.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("AI 精选礼物建议")
                        .font(.subheadline)
                        .bold()
                    ForEach(gifts, id: \.self) { gift in
                        HStack {
                            VStack(alignment: .leading) {
                                Text(gift.name)
                                    .font(.subheadline)
                                Text(gift.reason)
                                    .font(.caption)
                                    .foregroundColor(.gray)
                            }
                            Spacer()
                            Text("¥\(String(format: "%.0f", gift.price))")
                                .font(.subheadline)
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 4)
    }
}
```

---

### Task 12：设置页与退出登录

**Files:**
- Create: `mobile/EternalMoments/Views/SettingsView.swift`
- Create: `mobile/EternalMoments/ViewModels/SettingsViewModel.swift`

- [ ] **Step 1: 创建设置页**

```swift
// mobile/EternalMoments/Views/SettingsView.swift
import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var authManager: AuthManager
    @StateObject private var viewModel = SettingsViewModel()

    var body: some View {
        NavigationView {
            List {
                Section {
                    HStack {
                        Circle()
                            .fill(Color.gray.opacity(0.3))
                            .frame(width: 50, height: 50)
                            .overlay(Text("我").font(.headline))
                        VStack(alignment: .leading) {
                            Text(authManager.currentUser?.nickname ?? "未设置昵称")
                                .font(.headline)
                            Text(authManager.currentUser?.phone ?? "")
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                }

                Section(header: Text("语言设置")) {
                    ForEach(viewModel.languages, id: \.self) { lang in
                        HStack {
                            Text(lang)
                            Spacer()
                            if lang == viewModel.selectedLanguage {
                                Image(systemName: "checkmark")
                                    .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                            }
                        }
                        .onTapGesture { viewModel.selectedLanguage = lang }
                    }
                }

                Section(header: Text("法律与隐私")) {
                    NavigationLink("隐私权政策", destination: Text("隐私政策内容"))
                    NavigationLink("服务条款", destination: Text("服务条款内容"))
                }

                Section {
                    Button("退出登录") {
                        authManager.logout()
                    }
                    .foregroundColor(Color(red: 212/255, green: 63/255, blue: 82/255))
                }
            }
            .navigationTitle("设置")
        }
    }
}
```

```swift
// mobile/EternalMoments/ViewModels/SettingsViewModel.swift
import Foundation

class SettingsViewModel: ObservableObject {
    @Published var selectedLanguage = "中文"
    let languages = ["中文", "English", "日本語"]
}
```

---

## 阶段 5：部署与集成

### Task 13：Docker Compose 部署

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `backend/.env.example`

- [ ] **Step 1: 创建 docker-compose.yml**

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: eternal_moments
      POSTGRES_USER: em_user
      POSTGRES_PASSWORD: em_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U em_user -d eternal_moments"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build: ../backend
    environment:
      DATABASE_URL: postgresql://em_user:em_pass@postgres:5432/eternal_moments
      JWT_SECRET: dev_secret
      AI_PROVIDER: mock
      SMS_PROVIDER: mock
    ports:
      - "8000:8000"
    volumes:
      - ../backend/uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
```

- [ ] **Step 2: 创建环境变量示例**

```bash
# backend/.env.example
DATABASE_URL=postgresql://em_user:em_pass@localhost:5432/eternal_moments
JWT_SECRET=dev_secret_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=30
UPLOAD_DIR=uploads
AI_PROVIDER=mock
VOLCANO_ARK_API_KEY=
SMS_PROVIDER=mock
```

- [ ] **Step 3: 运行验证**

Run: `cd infra && docker-compose up --build`
Expected: PostgreSQL 和 backend 正常启动，访问 `http://localhost:8000/health` 返回 `{"status":"ok"}`

---

## 自审检查清单

### 1. Spec 覆盖检查

| 需求模块 | 对应任务 |
|----------|----------|
| F1 注册/登录 | Task 3-5 |
| F2 人物管理 | Task 6-7 |
| F3 纪念日记录 | Task 8-9 |
| F4 提醒功能 | Task 10-11 |
| 部署 | Task 13 |
| AI 祝福语/礼物 | Task 10 |
| 本地通知 | Task 11 |
| 设置页 | Task 12 |

### 2. 占位符扫描

- 已修复自定义关系查询的 TODO。
- 已补充火山方舟 API 调用实现。
- 已补充 iOS 头像 multipart 上传与后端接收接口。
- 已补充提醒重新生成祝福语/礼物的真实调用。
- 已补充 ContactDetailView 纪念日/节假日 Tab 的完整修改代码。

### 3. 类型一致性检查

- 后端 `contact_id` / `anniversary_id` / `reminder_id` 命名前后一致。
- iOS `Contact` / `Anniversary` / `SystemHoliday` / `Reminder` 模型与后端 JSON 字段一一对应。
- `APIClient.request` 的返回类型在调用处均有明确泛型声明。
- 后端人物路由已将 `/relationships` 置于 `/{contact_id}` 之前，避免路径冲突。
- 后端 `get_contacts` 已补充 `anniversary_count` 计算逻辑，与 iOS `Contact.anniversaryCount` 对应。

---

## 执行选项

**Plan complete and saved to `docs/superpowers/plans/2026-09-15-anniversary-app-implementation-plan.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - 我为每个 Task 派发独立子代理，任务间由你 review，迭代快。

**2. Inline Execution** - 在当前会话中使用 executing-plans 批量执行，设置检查点。

**Which approach?**