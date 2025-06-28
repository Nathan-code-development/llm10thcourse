# 雨林作业管理系统 - 项目架构

## 项目目录结构

```
llm0321_work_api/
│
├── alembic/              # 数据库迁移相关文件
│   └── versions/         # 数据库版本管理
│
├── app/                  # 应用主目录
│   ├── api/              # API路由
│   │   ├── deps.py       # 依赖项注入
│   │   ├── v1/           # API版本1
│   │   │   ├── endpoints/  # API端点
│   │   │   │   ├── assignments.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── classes.py
│   │   │   │   ├── courses.py
│   │   │   │   ├── gradings.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── statistics.py
│   │   │   │   ├── submissions.py
│   │   │   │   └── users.py
│   │   │   └── api.py      # API路由聚合
│   │   └── api.py        # API版本管理
│   │
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   ├── security.py   # 安全相关功能
│   │   └── settings.py   # 应用设置常量
│   │
│   ├── crud/             # 数据库CRUD操作
│   │   ├── base.py       # 基础CRUD操作
│   │   ├── assignment.py # 作业相关操作
│   │   ├── class_crud.py # 班级相关操作
│   │   ├── course.py     # 课程相关操作
│   │   ├── grading.py    # 批改相关操作
│   │   ├── notification.py # 通知相关操作
│   │   ├── submission.py # 提交相关操作
│   │   └── user.py       # 用户相关操作
│   │
│   ├── db/               # 数据库相关
│   │   ├── base.py       # 数据库基础配置
│   │   ├── init_db.py    # 数据库初始化
│   │   └── session.py    # 数据库会话
│   │
│   ├── models/           # 数据模型定义
│   │   ├── assignment.py # 作业模型
│   │   ├── class_model.py # 班级模型
│   │   ├── course.py     # 课程模型
│   │   ├── grading.py    # 批改模型
│   │   ├── notification.py # 通知模型
│   │   ├── submission.py # 提交模型
│   │   └── user.py       # 用户模型
│   │
│   ├── schemas/          # Pydantic模式验证
│   │   ├── assignment.py # 作业模式
│   │   ├── class_schema.py # 班级模式
│   │   ├── course.py     # 课程模式
│   │   ├── grading.py    # 批改模式
│   │   ├── msg.py        # 消息模式
│   │   ├── notification.py # 通知模式
│   │   ├── submission.py # 提交模式
│   │   ├── token.py      # 令牌模式
│   │   └── user.py       # 用户模式
│   │
│   ├── services/         # 业务逻辑服务
│   │   ├── assignment_service.py # 作业服务
│   │   ├── auth_service.py # 认证服务
│   │   ├── class_service.py # 班级服务
│   │   ├── course_service.py # 课程服务
│   │   ├── file_service.py # 文件服务
│   │   ├── grading_service.py # 批改服务
│   │   ├── notification_service.py # 通知服务
│   │   ├── statistics_service.py # 统计服务
│   │   ├── submission_service.py # 提交服务
│   │   └── user_service.py # 用户服务
│   │
│   ├── utils/            # 工具函数
│   │   ├── email.py      # 邮件相关
│   │   ├── storage.py    # 文件存储相关
│   │   └── tasks.py      # 异步任务相关
│   │
│   ├── worker.py         # Celery Worker配置
│   └── main.py           # 应用入口
│
├── docs/                 # 文档
│   ├── architecture.md   # 架构文档
│   └── api.md            # API文档
│
├── migrations/           # 数据库迁移脚本
│
├── tests/                # 测试
│   ├── conftest.py       # 测试配置
│   ├── api/              # API测试
│   └── crud/             # CRUD测试
│
├── .env                  # 环境变量(不提交到版本控制)
├── .gitignore            # Git忽略文件
├── alembic.ini           # Alembic配置
├── requirements.txt      # 项目依赖
└── README.md             # 项目说明
```

## 模块实现详情

### 1. 用户认证与权限管理

系统使用JWT实现身份验证和授权。用户登录后获取令牌，后续请求需要在头信息中包含此令牌。

认证流程:
1. 用户提交用户名和密码
2. 服务器验证凭据并生成JWT令牌
3. 客户端使用令牌进行后续API调用
4. 服务器验证令牌并检查相关权限

实现文件:
- `app/core/security.py`: JWT相关功能实现
- `app/api/deps.py`: 依赖项注入，包括当前用户获取
- `app/api/v1/endpoints/auth.py`: 认证相关API端点

### 2. 数据库模型

系统使用SQLModel作为ORM工具，结合FastAPI和Pydantic进行数据验证。

主要模型关系:
- 用户(User) - 1对多 -> 班级创建(Class)
- 班级(Class) - 多对多 -> 用户(User) (通过ClassMember)
- 教师(User) - 1对多 -> 课程(Course)
- 课程(Course) - 1对多 -> 作业(Assignment)
- 作业(Assignment) - 1对多 -> 提交(Submission)
- 学生(User) - 1对多 -> 提交(Submission)
- 提交(Submission) - 1对1 -> 批改(Grading)
- 教师(User) - 1对多 -> 批改(Grading)
- 用户(User) - 1对多 -> 通知(Notification)

### 3. 文件存储

系统支持将学生提交的作业文件保存到本地文件系统或云存储(如AWS S3或阿里云OSS)。

文件处理流程:
1. 学生上传作业文件
2. 服务器接收文件并处理(检查文件类型、大小等)
3. 文件保存至存储系统并生成访问URL
4. URL保存到数据库中与作业提交记录关联

实现文件:
- `app/utils/storage.py`: 文件存储相关功能
- `app/services/file_service.py`: 文件服务业务逻辑

### 4. 作业管理

作业管理模块实现教师发布作业和学生提交作业的功能。

作业发布流程:
1. 教师创建作业，设置标题、描述、截止日期等
2. 系统保存作业信息并通知相关学生
3. 学生查看作业详情和要求
4. 学生在截止日期前提交作业

实现文件:
- `app/api/v1/endpoints/assignments.py`: 作业相关API
- `app/api/v1/endpoints/submissions.py`: 提交相关API
- `app/services/assignment_service.py`: 作业服务业务逻辑
- `app/services/submission_service.py`: 提交服务业务逻辑

### 5. 批改功能

批改模块实现教师批改学生作业和学生查看反馈的功能。

批改流程:
1. 教师查看学生提交的作业
2. 教师给予评分和文字反馈
3. 系统记录批改结果并通知学生
4. 学生查看批改结果和反馈

实现文件:
- `app/api/v1/endpoints/gradings.py`: 批改相关API
- `app/services/grading_service.py`: 批改服务业务逻辑

### 6. 通知系统

通知系统实现系统到用户的消息通知功能，包括作业发布、批改完成等通知。

通知流程:
1. 系统事件触发通知(如新作业发布)
2. 系统创建通知记录并存入数据库
3. 用户请求或实时推送通知
4. 用户查看通知详情并标记为已读

实现文件:
- `app/api/v1/endpoints/notifications.py`: 通知相关API
- `app/services/notification_service.py`: 通知服务业务逻辑

### 7. 统计分析

统计分析模块提供数据分析功能，包括作业完成情况、成绩分析等。

实现文件:
- `app/api/v1/endpoints/statistics.py`: 统计相关API
- `app/services/statistics_service.py`: 统计服务业务逻辑

### 8. 异步任务处理

使用Celery处理耗时任务，如大文件上传、批量通知发送等。

实现文件:
- `app/utils/tasks.py`: 异步任务定义
- `app/worker.py`: Celery Worker配置

## 开发与部署

### 开发环境

1. Python 3.8+
2. MySQL 8.0+
3. Redis (用于Celery)

### 部署选项

1. **开发环境**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **生产环境**:
   - 使用Gunicorn作为WSGI服务器
   - 使用Nginx作为反向代理
   - 使用Supervisor管理进程
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

3. **Docker部署**:
   - 使用Docker Compose编排服务
   - 包含FastAPI应用、MySQL数据库、Redis和Celery Worker

## 扩展计划

1. **移动端支持**: 开发移动应用或响应式设计支持手机使用
2. **富文本编辑器**: 支持更丰富的作业内容编辑
3. **实时通知**: 使用WebSocket实现实时通知
4. **批量操作**: 支持批量评分和反馈
5. **在线讨论**: 支持作业相关讨论功能
6. **排行榜**: 实现班级或课程排行榜功能 