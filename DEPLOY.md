# Eternal Moments 部署指南

> 更新日期：2026-09-16  
> 适用版本：后端 FastAPI + PostgreSQL + iOS SwiftUI

---

## 一、Windows 本机开发/演示（不依赖 Docker）

### 前置条件

- Python 3.11+ 并已配置 pip
- PostgreSQL 15/16（本地或远程均可）
- 创建数据库和用户：

```sql
CREATE USER em_user WITH PASSWORD 'em_pass';
CREATE DATABASE eternal_moments OWNER em_user;
```

### 启动步骤

```powershell
cd backend

# 1. 安装依赖（首次）
pip install -r requirements.txt

# 2. 复制环境变量模板并修改
# Windows:
copy .env.example .env
# 按需编辑 .env，例如 DATABASE_URL/JWT_SECRET

# 3. 执行数据库迁移
alembic upgrade head

# 4. 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 验证

- 健康检查：`http://localhost:8000/health` → `{"status":"ok"}`
- API 文档：`http://localhost:8000/docs`
- 后端测试：`python -m pytest tests/ -q`（当前 65 个测试通过）

### 注意事项

- 本机若未安装 `apscheduler`，启动时会提示 `apscheduler 未安装，跳过定时任务启动`，API 仍可正常使用；定时任务需安装 `apscheduler` 后生效。
- 本地 PostgreSQL 若已占用 `5432`，请修改 `.env` 中的 `DATABASE_URL`。
- 头像上传会写入 `backend/uploads/avatars/`，目录会在首次上传时自动创建。

---

## 二、生产/云服务器 Docker Compose 部署

### 前置条件

- 一台 Linux 服务器（推荐阿里云 ECS / 腾讯云 CVM / 任意海外 VPS）
- Docker + Docker Compose 已安装
- 因本网络 Docker Hub 被墙，国内服务器需配置镜像加速器（见下方）

### 1. 配置 Docker 镜像加速器（国内服务器必做）

以阿里云镜像加速器为例：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://<你的加速器地址>.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

获取你的加速器地址：阿里云控制台 → 容器镜像服务 → 镜像工具 → 镜像加速器。

### 2. 复制代码到服务器

```bash
git clone https://github.com/lty296365742/eternal-moments.git
cd eternal-moments
```

### 3. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，至少修改以下两项：
#   JWT_SECRET=生产环境强随机字符串
#   DATABASE_URL 保持默认值即可（Docker 内部网络使用 postgres 主机名）
```

### 4. 启动服务

```bash
cd infra
docker compose up --build -d
```

### 5. 检查运行状态

```bash
# 查看容器日志
docker compose logs -f backend

# 验证健康检查
curl http://<服务器IP>:8000/health
```

### 6. 更新版本

```bash
cd infra
docker compose down
git pull
docker compose up --build -d
```

### 端口与安全

- 默认暴露端口：
  - `8000`：后端 API
  - `5432`：PostgreSQL（**生产环境建议关闭公网 5432，仅容器内部访问**）
- 建议前置 Nginx 反向代理，配置 HTTPS、速率限制、静态文件缓存
- 头像上传目录 `backend/uploads` 已挂载到容器 `/app/uploads`，建议定期备份

---

## 三、iOS App 连接后端

iOS 代码中需要把 `localhost` 替换为可访问的后端地址：

| 文件 | 当前值 | 修改建议 |
|------|--------|----------|
| `mobile/EternalMoments/Services/APIClient.swift` | `http://localhost:8000/api/v1/` | 改为服务器 IP 或域名 |
| `mobile/EternalMoments/Views/Components/AvatarView.swift` | `http://localhost:8000\(path)` | 改为服务器 IP 或域名 |
| `mobile/EternalMoments/ViewModels/AddContactViewModel.swift` | `http://localhost:8000/api/v1/contacts/upload/avatar` | 改为服务器 IP 或域名 |

**推荐**：把 base URL 提取成单个常量，避免散落三处。未来可用 Build Configuration 区分 dev/prod。

---

## 四、生产环境 checklist

- [ ] 修改 `JWT_SECRET` 为强随机字符串
- [ ] 关闭 PostgreSQL 的公网 5432 端口，或改绑内网 IP
- [ ] 配置 Nginx + HTTPS（Let's Encrypt 或阿里云 SSL）
- [ ] 配置 `AI_PROVIDER=volcano_ark` 并填写 `VOLCANO_ARK_API_KEY`
- [ ] 配置 `SMS_PROVIDER=aliyun` 并接入阿里云短信 SDK（需改造 `app/services/sms_service.py`）
- [ ] 头像存储迁移到阿里云 OSS（改造 `app/services/contact_service.py` upload_avatar）
- [ ] 设置定时任务监控、日志收集、数据库备份
- [ ] 处理安全清单：改密后令牌失效、手机号枚举统一报错、JWT_SECRET 启动校验

---

## 五、常见问题

**Q：Windows 上能跑 iOS 模拟器吗？**  
A：不能。iOS 模拟器/编译器只存在于 macOS。本仓库已配置 GitHub Actions，推送 `mobile/` 代码后自动在 macOS runner 上编译验证。

**Q：Docker Hub 拉不下来镜像怎么办？**  
A：国内服务器必须配置镜像加速器；海外服务器通常可直接拉取。本 Windows 开发机因网络限制无法本地 Docker 验证，但 `docker compose config` 已离线校验通过。

**Q：定时任务没运行？**  
A：检查容器内是否安装了 `apscheduler`（`requirements.txt` 已包含）；检查容器时区是否为东八区；检查日志中是否有 `处理纪念日...提醒时出错` 等异常。
