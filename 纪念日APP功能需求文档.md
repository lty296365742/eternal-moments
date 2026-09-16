# 纪念日APP功能需求文档

> 版本：V0.2
> 日期：2026-05-25
> 平台：iOS

---

## 一、功能拆分与依赖关系

### 1.1 功能模块总览

| 模块编号 | 模块名称 | 优先级 | 前置依赖 |
|---------|---------|--------|---------|
| F1 | 注册/登录 | P0（必须先做） | 无 |
| F2 | 人物管理 | P0（必须先做） | F1 |
| F3 | 纪念日记录 | P0（核心功能） | F1、F2 |
| F4 | 提醒功能 | P0（可后做） | F1、F2、F3 |

### 1.2 F1 注册/登录

| 编号 | 功能点 | 说明 | 优先级 |
|-----|-------|------|--------|
| F1.1 | 手机号注册 | 手机号+验证码注册 | P0 |
| F1.2 | 手机号登录 | 手机号+验证码/密码登录 | P0 |
| F1.3 | 密码设置与修改 | 注册时设置密码，登录后可修改 | P0 |
| F1.4 | Token鉴权 | 登录后下发Token，接口鉴权，若非手动退出，则token长期有效 | P0 |
| F1.5 | 自动登录 | Token有效期内自动登录，过期引导重新登录 | P0 |
| F1.6 | 退出登录 | 清除本地Token，跳转登录页 | P1 |

**依赖关系：** 无前置依赖，为所有后续功能的基础。

---

### 1.3 F2 人物管理

| 编号 | 功能点 | 说明 | 优先级 |
|-----|-------|------|--------|
| F2.1 | 新建人物 | 填写姓名、设置关系标签、上传头像、提醒状态（开启/关闭，默认开启）、填写备注 | P0 |
| F2.2 | 人物列表 | 展示所有已建人物，支持按关系筛选 | P0 |
| F2.3 | 查看人物详情 | 查看人物基本信息及关联的所有纪念日 | P0 |
| F2.4 | 编辑人物 | 修改姓名、关系、头像、提醒状态（开启/关闭）、备注 | P0 |
| F2.5 | 删除人物 | 删除人物及其关联的所有纪念日和提醒记录 | P0 |
| F2.6 | 关系标签管理 | 预置常用关系（父母、配偶、子女、朋友、同事等），支持自定义 | P0 |

**依赖关系：** 依赖F1（用户必须登录）。

---

### 1.4 F3 纪念日记录

| 编号 | 功能点 | 说明 | 优先级 |
|-----|-------|------|--------|
| F3.1 | 添加个人纪念日 | 选择人物，填写纪念日名称、日期、重复周期（每年/每月/仅一次） | P0 |
| F3.2 | 纪念日名称 | 预置常用名称（生日、结婚纪念日、忌日等），支持自定义 | P0 |
| F3.3 | 纪念日列表 | 展示人物关联的所有个人纪念日，按日期排序 | P0 |
| F3.4 | 编辑纪念日 | 修改纪念日名称、日期、重复周期 | P0 |
| F3.5 | 删除纪念日 | 删除指定纪念日 | P0 |
| F3.6 | 系统节假日展示 | 根据人物关系，展示系统自动关联的节假日列表 | P0 |
| F3.7 | 节假日提醒开关 | 用户可对每个人物的每个系统节假日单独开关提醒 | P0 |

**依赖关系：** 依赖F1、F2（必须先有用户和人物）。

---

### 1.5 F4 提醒功能

| 编号 | 功能点 | 说明 | 优先级 |
|-----|-------|------|--------|
| F4.1 | 系统节假日提醒 | 根据人物关系，提前3天推送提醒，附带AI生成的祝福语及海报 | P1 |
| F4.2 | 个人纪念日提醒 | 对用户记录的个人纪念日，提前5天推送提醒，附带AI推荐的礼物及购买链接 | P1 |
| F4.3 | 提醒记录列表 | 展示历史提醒记录，标记已读/未读状态 | P1 |
| F4.4 | 一键复制祝福语 | 复制AI生成的祝福语或海报图片到剪贴板 | P1 |
| F4.5 | 查看礼物推荐详情 | 展示推荐礼物的名称、价格、购买链接 | P1 |
| F4.6 | 本地通知推送 | 通过iOS本地通知实现定时推送提醒 | P1 |

**依赖关系：** 依赖F1、F2、F3（必须有用户、人物和纪念日数据）。

---

### 1.6 开发顺序建议

```
第一阶段（基础）：F1 注册/登录
    ↓
第二阶段（核心）：F2 人物管理
    ↓
第三阶段（核心）：F3 纪念日记录
    ↓
第四阶段（增值）：F4 提醒功能
```

---

## 二、后台接口设计

### 2.1 接口规范

| 项目 | 规范 |
|-----|------|
| 基础地址 | https://api.xxx.com/api/v1 |
| 请求格式 | application/json |
| 鉴权方式 | Bearer Token（Header: Authorization） |
| 通用响应 | {"code": 0, "message": "success", "data": {}} |
| 分页参数 | page（页码）、page_size（每页条数） |

### 2.2 接口列表

---

#### 2.2.1 认证模块

**① 发送验证码**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /auth/sms/send |
| 说明 | 发送注册/登录验证码 |

请求参数：
```json
{
  "phone": "13800138000",       // 手机号，必填
  "type": "register"            // register-注册, login-登录, reset-重置密码，必填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

**② 注册**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /auth/register |
| 说明 | 手机号+验证码注册 |

请求参数：
```json
{
  "phone": "13800138000",       // 手机号，必填
  "sms_code": "123456",         // 验证码，必填
  "password": "Abc123456",      // 密码，必填，6-20位
  "nickname": "用户昵称"         // 昵称，选填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U10001",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 604800
  }
}
```

---

**③ 登录**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /auth/login |
| 说明 | 手机号+密码或手机号+验证码登录 |

请求参数：
```json
{
  "phone": "13800138000",       // 手机号，必填
  "password": "Abc123456",      // 密码，与sms_code二选一
  "sms_code": "123456"          // 验证码，与password二选一
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U10001",
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 604800
  }
}
```

---

**④ 修改密码**

| 项目 | 内容 |
|-----|------|
| 地址 | PUT /auth/password |
| 说明 | 修改登录密码，需验证旧密码或验证码 |

请求参数：
```json
{
  "old_password": "Abc123456",  // 旧密码，与sms_code二选一
  "sms_code": "123456",         // 验证码，与old_password二选一
  "new_password": "Xyz789012"   // 新密码，必填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

#### 2.2.2 人物管理模块

**⑤ 获取人物列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /contacts |
| 说明 | 获取当前用户的所有人物，支持筛选和分页 |

请求参数（Query String）：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| relationship | string | 否 | 按关系筛选 |
| keyword | string | 否 | 按姓名搜索 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页条数，默认20 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 15,
    "list": [
      {
        "contact_id": "C10001",
        "name": "妈妈",
        "avatar": "https://cdn.xxx.com/avatar/C10001.jpg",
        "relationship": "母亲",
        "notes": "",
        "anniversary_count": 3,
        "created_at": "2026-05-01 10:00:00"
      }
    ]
  }
}
```

---

**⑥ 新建人物**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /contacts |
| 说明 | 创建新的人物档案 |

请求参数：
```json
{
  "name": "妈妈",               // 姓名，必填，最长20字
  "relationship": "母亲",       // 关系标签，必填
  "avatar": "base64字符串或URL", // 头像，选填
  "notes": "喜欢花"              // 备注，选填，最长200字
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "contact_id": "C10001",
    "name": "妈妈",
    "avatar": "https://cdn.xxx.com/avatar/C10001.jpg",
    "relationship": "母亲",
    "notes": "喜欢花",
    "created_at": "2026-05-01 10:00:00"
  }
}
```

---

**⑦ 获取人物详情**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /contacts/{contact_id} |
| 说明 | 获取指定人物的详细信息及关联纪念日 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "contact_id": "C10001",
    "name": "妈妈",
    "avatar": "https://cdn.xxx.com/avatar/C10001.jpg",
    "relationship": "母亲",
    "notes": "喜欢花",
    "anniversaries": [
      {
        "anniversary_id": "A10001",
        "title": "生日",
        "date": "03-15",
        "repeat_type": "yearly",
        "type": "personal",
        "days_remaining": 293,
        "created_at": "2026-05-01 10:00:00"
      }
    ],
    "system_holidays": [
      {
        "holiday_id": "H10003",
        "name": "母亲节",
        "date": "2026-05-10",
        "remind_enabled": true,
        "days_remaining": 0
      }
    ],
    "created_at": "2026-05-01 10:00:00"
  }
}
```

---

**⑧ 更新人物**

| 项目 | 内容 |
|-----|------|
| 地址 | PUT /contacts/{contact_id} |
| 说明 | 更新人物信息 |

请求参数：
```json
{
  "name": "妈妈",               // 姓名，选填
  "relationship": "母亲",       // 关系标签，选填
  "avatar": "base64字符串或URL", // 头像，选填
  "notes": "喜欢花和茶"          // 备注，选填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "contact_id": "C10001",
    "name": "妈妈",
    "avatar": "https://cdn.xxx.com/avatar/C10001.jpg",
    "relationship": "母亲",
    "notes": "喜欢花和茶",
    "updated_at": "2026-05-25 12:00:00"
  }
}
```

---

**⑨ 删除人物**

| 项目 | 内容 |
|-----|------|
| 地址 | DELETE /contacts/{contact_id} |
| 说明 | 删除人物及其关联的所有纪念日和提醒记录 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

**⑩ 获取关系标签列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /contacts/relationships |
| 说明 | 获取系统预置关系标签及用户自定义标签 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "preset": [
      {"key": "father", "label": "父亲"},
      {"key": "mother", "label": "母亲"},
      {"key": "spouse", "label": "配偶"},
      {"key": "child", "label": "子女"},
      {"key": "friend", "label": "朋友"},
      {"key": "colleague", "label": "同事"},
      {"key": "grandparent", "label": "祖父母/外祖父母"},
      {"key": "sibling", "label": "兄弟姐妹"},
      {"key": "teacher", "label": "老师"},
      {"key": "other", "label": "其他"}
    ],
    "custom": [
      {"key": "custom_1", "label": "干妈"}
    ]
  }
}
```

---

#### 2.2.3 纪念日记录模块

**⑪ 获取纪念日名称列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /anniversaries/templates |
| 说明 | 获取系统预置纪念日名称列表，供用户在添加纪念日时选择 |

请求参数：无

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "title_key": "birthday",
        "label": "生日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "wedding",
        "label": "结婚纪念日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "memorial",
        "label": "忌日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "love_start",
        "label": "相恋纪念日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "work_start",
        "label": "入职纪念日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "graduation",
        "label": "毕业纪念日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "move_in",
        "label": "搬家纪念日",
        "default_repeat": "once"
      },
      {
        "title_key": "baby_born",
        "label": "宝宝出生",
        "default_repeat": "yearly"
      },
      {
        "title_key": "adoption",
        "label": "领养纪念日",
        "default_repeat": "yearly"
      },
      {
        "title_key": "other",
        "label": "其他",
        "default_repeat": "yearly"
      }
    ]
  }
}
```

---

**⑫ 获取纪念日列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /anniversaries |
| 说明 | 获取指定人物的纪念日列表 | |

请求参数（Query String）：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| contact_id | string | 是 | 人物ID |
| type | string | 否 | 筛选类型：personal-个人 / holiday-系统节假日 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "anniversary_id": "A10001",
        "title": "生日",
        "date": "03-15",
        "repeat_type": "yearly",
        "type": "personal",
        "days_remaining": 293
      }
    ]
  }
}
```

---

**⑬ 添加个人纪念日**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /anniversaries |
| 说明 | 为指定人物添加个人纪念日 |

请求参数：
```json
{
  "contact_id": "C10001",       // 人物ID，必填
  "title_key": "birthday",      // 预置名称标识（与title二选一，优先使用title_key）
  "title": "生日",               // 自定义纪念日名称（title_key为"other"或未传时必填，最长30字）
  "date": "03-15",               // 日期，必填，格式MM-DD
  "repeat_type": "yearly"        // 重复方式：yearly-每年 / monthly-每月 / once-仅一次（不传时使用预置名称的默认值）
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "anniversary_id": "A10001",
    "title": "生日",
    "title_key": "birthday",
    "date": "03-15",
    "repeat_type": "yearly",
    "created_at": "2026-05-25 12:00:00"
  }
}
```

---

**⑭ 更新纪念日**

| 项目 | 内容 |
|-----|------|
| 地址 | PUT /anniversaries/{anniversary_id} |
| 说明 | 修改个人纪念日信息 |

请求参数：
```json
{
  "title_key": "birthday",      // 预置名称标识（与title二选一）
  "title": "生日",               // 自定义名称（选填）
  "date": "03-15",               // 选填
  "repeat_type": "yearly"        // 选填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "anniversary_id": "A10001",
    "title": "生日",
    "title_key": "birthday",
    "date": "03-15",
    "repeat_type": "yearly",
    "updated_at": "2026-05-25 12:00:00"
  }
}
```

---

**⑮ 删除纪念日**

| 项目 | 内容 |
|-----|------|
| 地址 | DELETE /anniversaries/{anniversary_id} |
| 说明 | 删除指定的个人纪念日 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

**⑯ 获取系统节假日列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /holidays |
| 说明 | 获取所有系统预置节假日 |

请求参数（Query String）：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| relationship | string | 否 | 按关系筛选适用节假日 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "holiday_id": "H10003",
        "name": "母亲节",
        "date": "2026-05-10",
        "applicable_relationships": ["母亲", "婆婆", "岳母"],
        "description": "每年5月第二个星期日"
      }
    ]
  }
}
```

---

**⑰ 设置节假日提醒开关**

| 项目 | 内容 |
|-----|------|
| 地址 | PUT /contacts/{contact_id}/holidays/{holiday_id}/remind |
| 说明 | 对指定人物的指定节假日开启或关闭提醒 |

请求参数：
```json
{
  "remind_enabled": true         // 是否开启提醒，必填
}
```

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

#### 2.2.4 提醒模块

**⑱ 获取提醒记录列表**

| 项目 | 内容 |
|-----|------|
| 地址 | GET /reminders |
| 说明 | 获取用户的提醒记录，支持筛选和分页 |

请求参数（Query String）：
| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| type | string | 否 | 筛选类型：holiday-节假日 / personal-个人纪念日 |
| status | string | 否 | 状态：unread-未读 / read-已读 |
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页条数，默认20 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 8,
    "list": [
      {
        "reminder_id": "R10001",
        "contact_id": "C10001",
        "contact_name": "妈妈",
        "anniversary_title": "母亲节",
        "type": "holiday",
        "remind_time": "2026-05-07 09:00:00",
        "event_date": "2026-05-10",
        "status": "unread",
        "blessing": "亲爱的妈妈，母亲节快乐...",
        "gifts": null,
        "created_at": "2026-05-07 09:00:00"
      },
      {
        "reminder_id": "R10002",
        "contact_id": "C10001",
        "contact_name": "妈妈",
        "anniversary_title": "生日",
        "type": "personal",
        "remind_time": "2026-03-10 09:00:00",
        "event_date": "2026-03-15",
        "status": "unread",
        "blessing": null,
        "gifts": [
          {
            "name": "兰蔻小黑瓶精华",
            "price": 799,
            "reason": "护肤品经典款，适合送给注重保养的妈妈",
            "purchase_url": "https://item.xxx.com/xxx"
          }
        ],
        "created_at": "2026-03-10 09:00:00"
      }
    ]
  }
}
```

---

**⑲ 标记提醒已读**

| 项目 | 内容 |
|-----|------|
| 地址 | PUT /reminders/{reminder_id}/read |
| 说明 | 标记指定提醒为已读 |

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": null
}
```

---

**⑳ 生成祝福语**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /reminders/{reminder_id}/blessing |
| 说明 | 针对节假日提醒，调用AI生成祝福语（服务端生成，仅节假日提醒调用） |

请求参数：无（服务端根据提醒信息自动生成）

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "blessing": "亲爱的妈妈，母亲节快乐！感谢您一直以来的付出与陪伴，愿您每天都被幸福环绕，永远年轻美丽。"
  }
}
```

---

**㉑ 推荐礼物**

| 项目 | 内容 |
|-----|------|
| 地址 | POST /reminders/{reminder_id}/gifts |
| 说明 | 针对个人纪念日提醒，调用AI推荐礼物（服务端生成，仅个人纪念日提醒调用） |

请求参数：无（服务端根据提醒信息自动生成）

响应：
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "gifts": [
      {
        "name": "兰蔻小黑瓶精华",
        "price": 799,
        "reason": "护肤品经典款，适合送给注重保养的妈妈",
        "purchase_url": "https://item.xxx.com/xxx"
      },
      {
        "name": "戴森吹风机",
        "price": 2999,
        "reason": "实用型礼品，提升生活品质",
        "purchase_url": "https://item.xxx.com/xxx"
      }
    ]
  }
}
```

---

## 三、数据库设计

### 3.1 ER关系图

```
t_user  1 ── N  t_contact  1 ── N  t_anniversary ── N ── 1  t_anniversary_template
                     │
                     1 ── N  t_contact_holiday
                                 │
                     t_system_holiday
                     (N ── 1)

t_user  1 ── N  t_reminder
```

### 3.2 表结构

---

#### t_user（用户表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| user_id | VARCHAR(32) | UNIQUE, NOT NULL | 用户唯一标识 |
| phone | VARCHAR(20) | UNIQUE, NOT NULL | 手机号 |
| password_hash | VARCHAR(128) | NOT NULL | 密码哈希 |
| nickname | VARCHAR(50) | DEFAULT NULL | 昵称 |
| avatar | VARCHAR(500) | DEFAULT NULL | 头像URL |
| status | TINYINT | DEFAULT 1 | 状态：1-正常 0-禁用 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

---

#### t_contact（人物档案表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| contact_id | VARCHAR(32) | UNIQUE, NOT NULL | 人物唯一标识 |
| user_id | VARCHAR(32) | FK→t_user.user_id, NOT NULL | 所属用户 |
| name | VARCHAR(50) | NOT NULL | 姓名 |
| avatar | VARCHAR(500) | DEFAULT NULL | 头像URL |
| relationship | VARCHAR(50) | NOT NULL | 关系标签 |
| notes | VARCHAR(500) | DEFAULT NULL | 备注 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引：**
- idx_contact_user_id ON (user_id)
- idx_contact_relationship ON (user_id, relationship)

---

#### t_system_holiday（系统节假日表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| holiday_id | VARCHAR(32) | UNIQUE, NOT NULL | 节假日唯一标识 |
| name | VARCHAR(50) | NOT NULL | 节假日名称 |
| date_rule | VARCHAR(100) | NOT NULL | 日期规则，如"05-02-SUNDAY"表示5月第2个周日 |
| applicable_relationships | JSON | NOT NULL | 适用关系列表，如["母亲","婆婆","岳母"] |
| description | VARCHAR(200) | DEFAULT NULL | 节假日描述 |
| status | TINYINT | DEFAULT 1 | 状态：1-启用 0-停用 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**预置数据示例：**

| name | date_rule | applicable_relationships |
|-----|-----------|------------------------|
| 母亲节 | 05-2-SUNDAY | ["母亲","婆婆","岳母"] |
| 父亲节 | 06-3-SUNDAY | ["父亲","公公","岳父"] |
| 情人节 | 02-14 | ["配偶","恋人"] |
| 七夕 | 07-07-LUNAR | ["配偶","恋人"] |
| 儿童节 | 06-01 | ["子女"] |
| 教师节 | 09-10 | ["老师"] |
| 春节 | SPRING-FESTIVAL | ["父亲","母亲","配偶","子女","兄弟姐妹","祖父母/外祖父母"] |
| 端午节 | DRAGON-BOAT | ["父亲","母亲","配偶","子女","兄弟姐妹","祖父母/外祖父母"] |
| 中秋节 | MID-AUTUMN | ["父亲","母亲","配偶","子女","兄弟姐妹","祖父母/外祖父母"] |

**索引：**
- idx_holiday_name ON (name)

---

#### t_anniversary_template（纪念日名称预置表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| title_key | VARCHAR(32) | UNIQUE, NOT NULL | 名称标识 |
| label | VARCHAR(50) | NOT NULL | 显示名称 |
| default_repeat | VARCHAR(20) | DEFAULT 'yearly' | 默认重复方式：yearly/monthly/once |
| sort_order | INT | DEFAULT 0 | 排序权重，越小越靠前 |
| status | TINYINT | DEFAULT 1 | 状态：1-启用 0-停用 |
| created_at | DATETIME | NOT NULL | 创建时间 |

**预置数据：**

| title_key | label | default_repeat |
|-----------|-------|----------------|
| birthday | 生日 | yearly |
| wedding | 结婚纪念日 | yearly |
| memorial | 忌日 | yearly |
| love_start | 相恋纪念日 | yearly |
| work_start | 入职纪念日 | yearly |
| graduation | 毕业纪念日 | yearly |
| move_in | 搬家纪念日 | once |
| baby_born | 宝宝出生 | yearly |
| adoption | 领养纪念日 | yearly |
| other | 其他 | yearly |

**索引：**
- idx_template_sort ON (sort_order, status)

---

#### t_anniversary（个人纪念日表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| anniversary_id | VARCHAR(32) | UNIQUE, NOT NULL | 纪念日唯一标识 |
| contact_id | VARCHAR(32) | FK→t_contact.contact_id, NOT NULL | 关联人物 |
| user_id | VARCHAR(32) | FK→t_user.user_id, NOT NULL | 所属用户（冗余，便于查询） |
| title | VARCHAR(50) | NOT NULL | 纪念日名称（选择预置时自动填入，自定义时由用户输入） |
| title_key | VARCHAR(32) | DEFAULT NULL | 关联预置名称标识（使用预置时有值，自定义时为NULL） |
| month_day | VARCHAR(5) | NOT NULL | 日期，格式MM-DD |
| repeat_type | VARCHAR(20) | NOT NULL | 重复方式：yearly/monthly/once |
| next_date | DATE | NOT NULL | 下一次日期（服务端计算维护） |
| status | TINYINT | DEFAULT 1 | 状态：1-正常 0-删除 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**索引：**
- idx_anniversary_contact ON (contact_id)
- idx_anniversary_user ON (user_id)
- idx_anniversary_next_date ON (user_id, next_date)
- idx_anniversary_title_key ON (title_key)

---

#### t_contact_holiday（人物-节假日关联表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| contact_id | VARCHAR(32) | FK→t_contact.contact_id, NOT NULL | 人物ID |
| holiday_id | VARCHAR(32) | FK→t_system_holiday.holiday_id, NOT NULL | 节假日ID |
| user_id | VARCHAR(32) | FK→t_user.user_id, NOT NULL | 所属用户（冗余） |
| remind_enabled | TINYINT | DEFAULT 1 | 是否开启提醒：1-开启 0-关闭 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

**唯一约束：** UNIQUE (contact_id, holiday_id)

**索引：**
- idx_ch_user ON (user_id)
- idx_ch_remind ON (user_id, remind_enabled)

---

#### t_reminder（提醒记录表）

| 字段 | 类型 | 约束 | 说明 |
|-----|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| reminder_id | VARCHAR(32) | UNIQUE, NOT NULL | 提醒唯一标识 |
| user_id | VARCHAR(32) | FK→t_user.user_id, NOT NULL | 所属用户 |
| contact_id | VARCHAR(32) | FK→t_contact.contact_id, NOT NULL | 关联人物 |
| type | VARCHAR(20) | NOT NULL | 类型：holiday-系统节假日 / personal-个人纪念日 |
| anniversary_id | VARCHAR(32) | DEFAULT NULL | 关联纪念日ID（type=personal时有值） |
| holiday_id | VARCHAR(32) | DEFAULT NULL | 关联节假日ID（type=holiday时有值） |
| event_title | VARCHAR(50) | NOT NULL | 提醒事件标题 |
| event_date | DATE | NOT NULL | 实际事件日期 |
| remind_time | DATETIME | NOT NULL | 提醒推送时间 |
| status | VARCHAR(20) | DEFAULT 'unread' | 状态：unread-未读 / read-已读 |
| blessing | TEXT | DEFAULT NULL | AI生成的祝福语（type=holiday时生成） |
| gifts | JSON | DEFAULT NULL | AI推荐的礼物列表（type=personal时生成） |
| created_at | DATETIME | NOT NULL | 创建时间 |

**索引：**
- idx_reminder_user ON (user_id)
- idx_reminder_user_status ON (user_id, status)
- idx_reminder_user_type ON (user_id, type)
- idx_reminder_time ON (remind_time)

---

## 四、AI系统提示词

### 4.1 祝福语生成系统提示词

```
# 角色设定

你是一位拥有20年情感表达经验的高级情感专家。你的核心能力是为不同亲密关系的人群撰写真挚、自然的祝福语。

# 你的职责

根据用户与接收者的关系、节假日类型，生成一段祝福语。祝福语将用于用户发送给对应的亲朋好友。

# 核心原则

1. 真诚自然：避免空洞的套话和堆砌辞藻。祝福语应当像是一个真正在意对方的人会说的话，而非模板化量产的内容。

2. 分寸得当：根据关系亲密程度调整语言风格。对父母可以深情但不煽情，对朋友可以轻松但不随意，对同事可以得体但不疏远。

3. 场景贴合：祝福语必须与节假日/纪念日的氛围契合。春节侧重团圆和新年期许，母亲节侧重感恩和陪伴，生日侧重个人祝愿和美好期许。

4. 长度适中：生成2-4句话，总字数控制在50-120字之间。

5. 语言禁忌：禁止使用"祝您福如东海寿比南山"等陈旧表达；禁止出现表情符号；禁止使用任何网络流行语或谐音梗。

# 输入信息

系统会提供以下信息，你需据此生成祝福语：
- 接收者与用户的关系：如"母亲"、"配偶"、"朋友"等
- 节假日名称：如"母亲节"、"春节"等
- 接收者称呼/姓名：如"妈妈"、"老王"等

# 输出要求

直接输出祝福语正文，不需要任何前缀、标题或解释说明。仅输出纯文本。
```

---

### 4.2 礼物推荐系统提示词

```
# 角色设定

你是一位在全平台拥有百万粉丝的资深礼物选品博主，专注于为不同关系的收礼人推荐高性价比、有诚意的礼品。你的选品风格注重实用性与心意并重，拒绝华而不实。

# 你的职责

根据用户与收礼人的关系、纪念日类型，推荐3-5款适合的礼品，每款礼品需附带推荐理由和参考价格。

# 核心原则

1. 因人选礼：根据关系和纪念日类型匹配礼物品类。送长辈侧重健康养生和实用型，送伴侣侧重浪漫和品质生活，送朋友侧重趣味和性价比，送同事侧重得体和不越界。

2. 品质优先：推荐知名度较高、口碑较好的品牌和产品，优先选择京东、天猫等主流电商平台的在售商品。不做小众冷门推荐，不推荐山寨或无品牌产品。

3. 价格合理：推荐商品价格应与关系匹配。长辈礼物价格区间300-2000元，伴侣礼物200-3000元，朋友礼物100-500元，同事礼物100-300元。在合理预算内追求品质。

4. 理由充分：每个推荐需说明推荐理由，理由需具体指向收礼人的需求、偏好或生活场景，而非泛泛的"好看"、"好用"。

5. 真实客观：只推荐你了解的产品，不编造产品信息。如对某一品类把握不大，宁可不推荐也不要编造虚假商品信息。

# 输入信息

系统会提供以下信息，你需据此推荐礼品：
- 收礼人与用户的关系：如"母亲"、"配偶"、"朋友"等
- 纪念日类型：如"生日"、"结婚纪念日"等
- 收礼者称呼/姓名：如"妈妈"、"妻子"等

# 输出格式

严格按以下JSON数组格式输出，不要输出任何其他内容：
[
  {
    "name": "商品名称",
    "price": 参考价格（数字，单位元）,
    "reason": "推荐理由（一句话，20-50字）",
    "purchase_url": "推荐购买链接（主流电商平台链接）"
  }
]

注意：只输出JSON数组，不要加markdown代码块标记，不要输出任何解释文字。
```
