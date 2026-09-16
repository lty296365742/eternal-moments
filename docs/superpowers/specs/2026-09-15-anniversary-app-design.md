# 纪念日APP 设计方案

> 版本：V1.0  
> 日期：2026-09-15  
> 状态：待评审

---

## 1. 项目背景与目标

### 1.1 背景

本项目为 iOS 平台纪念日管理应用，内部代号 **Eternal Moments**。用户可通过手机号注册登录，管理重要人物（家人、朋友、同事等），记录与该人物相关的个人纪念日，并由系统根据人物关系自动关联节假日。应用在事件来临前通过本地通知提醒用户，同时提供 AI 生成的祝福语与礼物推荐。

### 1.2 参考文档

- 需求文档：`C:\Users\29636\Desktop\个人\claude-workspace\ai-daily-tasks-workspace\纪念日APP\纪念日APP功能需求文档.md`
- UI 设计：`C:\Users\29636\Desktop\个人\claude-workspace\ai-daily-tasks-workspace\纪念日APP\UIDesignByGoogleStitch\stitch_`
- 设计系统：`UIDesignByGoogleStitch\stitch_\eternal_moments\DESIGN.md`

### 1.3 核心目标

1. 实现手机号注册/登录、Token 鉴权与自动登录。
2. 实现人物档案的增删改查、关系标签、头像上传。
3. 实现个人纪念日的增删改查、系统节假日展示、提醒开关。
4. 实现提醒记录的生成、列表展示、AI 祝福语、AI 礼物推荐与本地通知。
5. 提供可本地运行的开发环境，并预留向阿里云 ECS 迁移的部署路径。

### 1.4 非目标

- 不做社交分享、好友关系链、多语言完整本地化。
- 不做付费会员、积分、商城等商业模块。
- 生产环境的域名、SSL、CDN、App Store 上架不在本次实现范围内。

---

## 2. 总体架构

采用 **单仓库清晰单体架构**。前后端代码、基础设施脚本置于同一仓库，便于开发、测试与后续迁移。

```
纪念日APP/
├── mobile/                  # SwiftUI iOS App
│   ├── EternalMoments/
│   │   ├── App/
│   │   ├── Views/
│   │   ├── ViewModels/
│   │   ├── Services/
│   │   ├── Models/
│   │   └── Resources/
│   └── EternalMoments.xcodeproj
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 模型
│   │   ├── core/            # 配置、安全、依赖
│   │   └── main.py
│   ├── alembic/             # 数据库迁移
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── infra/                   # 基础设施
│   ├── docker-compose.yml
│   └── deploy/              # 生产部署脚本
└── docs/                    # 项目文档
    └── superpowers/specs/   # 设计文档
```

### 2.1 通信协议

- 前后端通过 **REST API + JSON** 通信。
- 鉴权使用 **Bearer Token**，通过 `Authorization: Bearer <token>` 请求头传递。
- Token 长期有效，除非用户手动退出登录。

### 2.2 部署方式

- **开发环境**：`docker-compose up` 一键启动 PostgreSQL + 后端服务；iOS App 通过 Xcode 在模拟器或真机运行。
- **生产环境**：迁移至阿里云 ECS，使用阿里云 RDS for PostgreSQL、阿里云 OSS（头像存储）、阿里云短信服务。

---

## 3. 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| iOS 前端 | SwiftUI | 原生 iOS 开发，严格遵循 UI 设计稿中的 iOS 风格 |
| 本地存储 | Keychain + SwiftData/UserDefaults | Keychain 存储 Token；SwiftData/UserDefaults 存储用户设置 |
| 网络 | URLSession + async/await | 自封装 `APIClient` 统一处理请求、Token、错误 |
| 后端框架 | FastAPI (Python 3.11) | 高性能、类型安全、自动生成 API 文档 |
| ORM | SQLAlchemy 2.0 | 数据库模型与迁移 |
| 数据库迁移 | Alembic | 管理表结构变更 |
| 数据库 | PostgreSQL 15 | 关系型数据持久化 |
| 定时任务 | APScheduler | 每日扫描生成提醒记录 |
| AI 服务 | 火山方舟 | 生成祝福语与礼物推荐 |
| 短信服务 | 开发期 Mock / 生产阿里云短信 | 开发期固定验证码，生产替换 SDK |
| 文件存储 | 本地磁盘 / 阿里云 OSS | 开发期本地，生产 OSS |
| 容器化 | Docker + docker-compose | 统一开发/生产运行环境 |

---

## 4. 后端设计

### 4.1 模块划分

后端按业务领域划分为 5 个路由模块：

| 模块 | 路径前缀 | 职责 |
|------|----------|------|
| 认证 | `/api/v1/auth` | 短信验证码、注册、登录、修改密码 |
| 人物 | `/api/v1/contacts` | 人物 CRUD、关系标签、头像 |
| 纪念日 | `/api/v1/anniversaries` | 个人纪念日 CRUD、纪念日模板 |
| 节假日 | `/api/v1/holidays` | 系统节假日、人物节假日提醒开关 |
| 提醒 | `/api/v1/reminders` | 提醒记录列表、已读、AI 生成 |

### 4.2 分层结构

```
routers/      -> 接收 HTTP 请求，参数校验，调用 services
services/     -> 业务逻辑，事务控制，调用 models/AI/SMS
models/       -> SQLAlchemy ORM 模型
schemas/      -> Pydantic 请求/响应模型
core/         -> 配置、数据库会话、JWT、异常处理
```

### 4.3 认证与安全

- 密码使用 `bcrypt` 哈希存储。
- JWT Token 使用 `PyJWT` 生成，包含 `user_id`、`phone`、`exp`。
- Token 有效期设置为 30 天（需求文档中“长期有效”的工程折中），过期后引导用户重新登录。
- 短信验证码开发期为 Mock：任意手机号输入 `123456` 即可通过；生产环境接入阿里云短信 SDK。
- 手机号格式校验：中国大陆手机号正则。

### 4.4 头像存储

- 开发期：上传至后端 `uploads/avatars/` 目录，通过 `/uploads/<filename>` 访问。
- 生产期：上传至阿里云 OSS，数据库存储 OSS 完整 URL。

### 4.5 定时提醒任务

每天 09:00 执行一次扫描：

1. 扫描所有启用的个人纪念日，计算 `next_date`。
2. 若距离 `next_date` 为 5 天，生成 `type=personal` 的提醒记录。
3. 扫描所有人物关联的系统节假日，若距离节假日为 3 天，生成 `type=holiday` 的提醒记录。
4. 生成提醒时，异步调用 AI 服务填充 `blessing` 或 `gifts`。
5. 后端仅生成提醒记录；移动端在同步到未读提醒后，使用 `UNUserNotificationCenter` 在设备本地调度通知。

### 4.6 AI 服务集成

- 封装统一 `AIClient` 接口，便于后续切换模型。
- 火山方舟实现：`volcano_ark_client.py`，调用大模型生成文本。
- 开发期默认使用 `MockAIClient` 返回固定示例内容；配置真实火山方舟 Key 后自动切换为真实调用。
- 礼物推荐要求模型按指定 JSON 数组格式输出，后端解析后入库。
- 祝福语生成按需求文档中的系统提示词拼接 Prompt。

---

## 5. 移动端设计

### 5.1 页面结构

| 页面 | SwiftUI View | 主要功能 |
|------|--------------|----------|
| 登录 | `LoginView` | 手机号 + 密码/验证码登录 |
| 注册 | `RegisterView` | 手机号 + 验证码 + 密码注册 |
| 联系人列表 | `ContactsListView` | 即将到来横滑卡片、搜索、分组列表、底部导航 |
| 联系人详情 | `ContactDetailView` | 头像/姓名/关系、纪念日/节假日 Tab |
| 添加/编辑联系人 | `AddContactView` | 头像上传、姓名、关系标签、智能提醒开关、备注 |
| 添加/编辑纪念日 | `AddAnniversaryView` | 关联联系人、纪念日类型、日期滚轮、重复频率 |
| 提醒列表 | `RemindersView` | 节假日祝福语卡片、个人礼物推荐、已读/未读 |
| 设置 | `SettingsView` | 个人档案、语言、隐私条款、退出登录 |

### 5.2 状态管理

- 使用 `Observable` / `ObservedObject` 的 MVVM 模式。
- `AuthManager`：全局登录状态、Token 读写、自动登录判断。
- `APIClient`：单例，负责网络请求、Token 注入、统一错误处理。
- 每个页面拥有独立 `ViewModel`，通过 `@StateObject` 或 `@ObservedObject` 绑定。

### 5.3 网络层

- 封装 `APIClient.request<T: Decodable>(method:path:body:)`。
- Token 过期时跳转登录页。
- 统一错误提示：网络错误、业务错误码、服务端异常。

### 5.4 本地通知

- 使用 `UNUserNotificationCenter`。
- 应用启动或刷新提醒列表时，从后端拉取未读提醒，并在设备本地为 `remind_time` 调度通知。
- 用户点击通知进入 `RemindersView`。

---

## 6. 数据库设计

直接使用需求文档中的数据库表结构，主要表包括：

- `t_user`：用户表
- `t_contact`：人物档案表
- `t_system_holiday`：系统节假日表
- `t_anniversary_template`：纪念日名称预置表
- `t_anniversary`：个人纪念日表
- `t_contact_holiday`：人物-节假日关联表
- `t_reminder`：提醒记录表

### 6.1 关键设计点

- `t_anniversary.next_date` 由后端在创建/更新时计算并维护。
- `t_contact_holiday` 在创建人物时根据关系自动插入系统节假日关联，默认 `remind_enabled=1`。
- `t_reminder.gifts` 和 `t_reminder.blessing` 为可空，根据 `type` 字段填充。

---

## 7. 部署方案

### 7.1 开发环境

通过 `infra/docker-compose.yml` 启动：

```yaml
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

  backend:
    build: ../backend
    environment:
      DATABASE_URL: postgresql://em_user:em_pass@postgres:5432/eternal_moments
      JWT_SECRET: dev_secret
      AI_PROVIDER: mock
    ports:
      - "8000:8000"
    volumes:
      - ../backend/uploads:/app/uploads
    depends_on:
      - postgres
```

启动命令：

```bash
cd infra
docker-compose up --build
```

### 7.2 生产迁移

迁移到阿里云时：

1. 后端服务部署到 ECS，使用相同 Dockerfile 构建运行。
2. PostgreSQL 替换为阿里云 RDS for PostgreSQL，修改 `DATABASE_URL`。
3. 头像存储替换为阿里云 OSS，修改文件上传逻辑。
4. 短信服务替换为阿里云短信 SDK，修改 `SMS_PROVIDER`。
5. AI 服务配置火山方舟生产 key。
6. 配置域名、HTTPS、Nginx 反向代理。

---

## 8. 开发阶段

按需求文档建议的顺序分四阶段实现：

### 阶段 1：F1 登录注册
- 后端：`auth` 路由、用户模型、JWT、Mock 短信。
- 前端：`LoginView`、`RegisterView`、`AuthManager`、启动自动登录。
- 验收：能注册、登录、Token 持久化、退出登录。

### 阶段 2：F2 人物管理
- 后端：`contacts` 路由、关系标签、头像上传。
- 前端：`ContactsListView`、`ContactDetailView`、`AddContactView`。
- 验收：能增删改查人物、上传头像、按关系筛选。

### 阶段 3：F3 纪念日记录
- 后端：`anniversaries`、`holidays` 路由、纪念日模板、系统节假日关联。
- 前端：联系人详情中的纪念日/节假日 Tab、`AddAnniversaryView`。
- 验收：能添加/编辑/删除个人纪念日、开关节假日提醒。

### 阶段 4：F4 提醒功能
- 后端：定时任务生成提醒、AI 祝福语/礼物、提醒列表接口。
- 前端：`RemindersView`、本地通知、祝福语复制、礼物详情。
- 验收：提醒提前生成、AI 内容可展示、本地通知正常触发。

---

## 9. 测试策略

### 9.1 后端测试

- 使用 `pytest`。
- 覆盖：routers、services、AI 客户端解析、定时任务逻辑。
- 数据库测试使用 `pytest-postgresql` 启动临时 PostgreSQL 实例，确保测试环境与生产一致。

### 9.2 前端测试

- 使用 `XCTest`。
- 覆盖：`APIClient` 请求与错误处理、`AuthManager` 状态、`ViewModel` 数据转换。
- UI 测试覆盖主要用户流程：登录 → 添加联系人 → 添加纪念日 → 查看提醒。

---

## 10. 风险与待确认事项

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 火山方舟 API 稳定性 | AI 功能不可用 | 设计 `AIClient` 抽象层，可快速切换模型 |
| iOS 本地通知权限 | 用户拒绝后无法提醒 | 首次进入应用时引导授权，提供设置页跳转 |
| 农历/节假日日期规则复杂 | 系统节假日计算错误 | 先实现固定日期规则，复杂农历规则后续迭代 |
| 头像本地存储在生产环境不适用 | 迁移时需要改造 | 抽象 `StorageClient`，开发期与生产期分别实现 |

---

## 11. 成功标准

1. 所有 F1-F4 功能按需求文档实现并通过手动验收。
2. 后端测试覆盖率 ≥ 60%，关键服务（auth、contacts、anniversaries、reminders）≥ 80%。
3. iOS App 能在 Xcode 模拟器稳定运行，主要流程无崩溃。
4. `docker-compose up` 能在干净环境中 5 分钟内启动完整后端+数据库。
5. 代码结构清晰，新增开发者能在 30 分钟内理解目录与运行方式。

---

*文档作者：Claude Code*  
*待评审人：项目需求方*