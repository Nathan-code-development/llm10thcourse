# 声声作业管理系统

## 项目介绍

声声作业管理系统是一个基于FastAPI开发的在线作业提交与批改平台，旨在为师生提供便捷的作业管理解决方案。系统支持学生上传作业、教师批改评分、多班级多课程管理等核心功能。

## 软件架构

- **后端框架**：FastAPI
- **数据库**：MySQL
- **ORM**：SQLModel
- **认证**：JWT (JSON Web Token)
- **文件存储**：本地文件系统/AWS S3/阿里云OSS
- **任务队列**：Celery (用于处理文件上传、通知发送等异步任务)

## 系统功能

### 用户角色及功能

1. **管理员**
   - 管理用户账户（教师和学生）
   - 创建和管理班级
   - 查看系统日志
   - 系统设置

2. **教师**
   - 创建课程
   - 在课程中发布作业
   - 查看学生提交的作业
   - 批改作业并给予评分和反馈
   - 查看班级和个人的作业统计
   - 发送通知给学生

3. **学生**
   - 查看所有课程和对应作业
   - 上传作业提交
   - 查看老师的批改结果和反馈
   - 跟踪个人作业完成情况

### 核心功能模块

1. **用户管理模块**
   - 用户注册、登录、找回密码
   - 个人信息管理
   - 权限控制

2. **班级管理模块**
   - 创建班级
   - 管理班级成员
   - 班级信息查看

3. **课程管理模块**
   - 创建和编辑课程
   - 关联班级和课程
   - 课程内容管理

4. **作业管理模块**
   - 发布作业
   - 设置截止日期
   - 作业要求描述
   - 支持附件

5. **作业提交模块**
   - 学生提交作业
   - 支持多种文件格式
   - 记录提交时间
   - 支持重新提交

6. **作业批改模块**
   - 查看学生提交的作业
   - 给予评分
   - 添加文字反馈
   - 标记常见错误

7. **统计分析模块**
   - 作业完成情况统计
   - 成绩分析
   - 班级整体情况分析

8. **通知系统**
   - 新作业发布通知
   - 作业批改完成通知
   - 作业截止提醒

## 数据库设计

### 主要数据表

1. **用户表(users)**
   - id: 用户ID
   - username: 用户名
   - email: 邮箱
   - password_hash: 密码哈希
   - role: 角色(admin/teacher/student)
   - created_at: 创建时间
   - updated_at: 更新时间

2. **班级表(classes)**
   - id: 班级ID
   - name: 班级名称
   - description: 班级描述
   - created_at: 创建时间
   - created_by: 创建者ID

3. **班级成员表(class_members)**
   - id: 记录ID
   - class_id: 班级ID
   - user_id: 用户ID
   - role: 角色(teacher/student)
   - joined_at: 加入时间

4. **课程表(courses)**
   - id: 课程ID
   - name: 课程名称
   - description: 课程描述
   - class_id: 所属班级ID
   - teacher_id: 教师ID
   - status: 状态(active/archived)
   - created_at: 创建时间
   - updated_at: 更新时间

5. **作业表(assignments)**
   - id: 作业ID
   - title: 作业标题
   - description: 作业描述
   - course_id: 所属课程ID
   - due_date: 截止日期
   - total_points: 总分值
   - attachment_url: 附件URL
   - created_at: 创建时间
   - updated_at: 更新时间

6. **作业提交表(submissions)**
   - id: 提交ID
   - assignment_id: 作业ID
   - student_id: 学生ID
   - submission_time: 提交时间
   - file_url: 文件URL
   - status: 状态(submitted/graded)
   - comments: 学生备注

7. **批改表(gradings)**
   - id: 批改ID
   - submission_id: 提交ID
   - teacher_id: 教师ID
   - score: 评分
   - feedback: 反馈
   - graded_at: 批改时间
   - updated_at: 更新时间

8. **通知表(notifications)**
   - id: 通知ID
   - user_id: 接收用户ID
   - title: 通知标题
   - content: 通知内容
   - type: 类型(assignment/feedback/reminder)
   - is_read: 是否已读
   - created_at: 创建时间

## API设计

### 认证相关
- POST /api/auth/login - 用户登录
- POST /api/auth/register - 用户注册
- POST /api/auth/refresh-token - 刷新令牌
- POST /api/auth/change-password - 修改密码

### 用户管理
- GET /api/users - 获取用户列表(管理员)
- GET /api/users/{user_id} - 获取用户详情
- PUT /api/users/{user_id} - 更新用户信息
- DELETE /api/users/{user_id} - 删除用户(管理员)

### 班级管理
- POST /api/classes - 创建班级
- GET /api/classes - 获取班级列表
- GET /api/classes/{class_id} - 获取班级详情
- PUT /api/classes/{class_id} - 更新班级信息
- DELETE /api/classes/{class_id} - 删除班级
- POST /api/classes/{class_id}/members - 添加班级成员
- GET /api/classes/{class_id}/members - 获取班级成员
- DELETE /api/classes/{class_id}/members/{user_id} - 移除班级成员

### 课程管理
- POST /api/courses - 创建课程
- GET /api/courses - 获取课程列表
- GET /api/courses/{course_id} - 获取课程详情
- PUT /api/courses/{course_id} - 更新课程信息
- DELETE /api/courses/{course_id} - 删除课程
- GET /api/classes/{class_id}/courses - 获取班级课程

### 作业管理
- POST /api/assignments - 创建作业
- GET /api/assignments - 获取作业列表
- GET /api/assignments/{assignment_id} - 获取作业详情
- PUT /api/assignments/{assignment_id} - 更新作业信息
- DELETE /api/assignments/{assignment_id} - 删除作业
- GET /api/courses/{course_id}/assignments - 获取课程作业

### 作业提交
- POST /api/submissions - 提交作业
- GET /api/submissions - 获取提交列表
- GET /api/submissions/{submission_id} - 获取提交详情
- DELETE /api/submissions/{submission_id} - 删除提交
- GET /api/assignments/{assignment_id}/submissions - 获取作业提交列表
- GET /api/users/{user_id}/submissions - 获取用户提交列表

### 作业批改
- POST /api/gradings - 批改作业
- GET /api/gradings/{grading_id} - 获取批改详情
- PUT /api/gradings/{grading_id} - 更新批改信息
- GET /api/submissions/{submission_id}/gradings - 获取提交批改

### 通知管理
- GET /api/notifications - 获取通知列表
- GET /api/notifications/{notification_id} - 获取通知详情
- PUT /api/notifications/{notification_id}/read - 标记通知为已读
- DELETE /api/notifications/{notification_id} - 删除通知

### 统计分析
- GET /api/statistics/assignments/{assignment_id} - 获取作业统计
- GET /api/statistics/courses/{course_id} - 获取课程统计
- GET /api/statistics/users/{user_id} - 获取用户统计
- GET /api/statistics/classes/{class_id} - 获取班级统计

## 系统安全与性能

1. **安全措施**
   - JWT认证
   - 密码加盐哈希存储
   - CORS配置
   - 角色权限控制
   - 防SQL注入

2. **性能优化**
   - 数据库索引优化
   - 使用异步任务处理大文件上传
   - 分页加载大数据列表
   - 缓存常用数据

3. **扩展性**
   - 模块化设计
   - 微服务架构预留

## 安装教程

1. 克隆仓库
```bash
git clone https://gitee.com/your-username/llm0321_work_api.git
cd llm0321_work_api
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
```bash
# 修改 app/core/config.py 中的数据库配置
# 执行数据库迁移
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

5. 启动服务
```bash
uvicorn app.main:app --reload
```

## 使用说明

1. 访问 http://localhost:8000/docs 查看API文档
2. 使用管理员账户登录并创建初始班级和课程
3. 邀请教师和学生加入系统
4. 教师发布作业，学生提交作业，教师批改作业

## 参与贡献

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

#### 特技

1. 使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2. Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3. 你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4. [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5. Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6. Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
