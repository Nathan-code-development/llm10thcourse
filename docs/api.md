# 雨林作业管理系统 - API文档

## API概述

本文档描述雨林作业管理系统的RESTful API接口。所有API都以`/api`为基础路径，使用JSON格式进行数据交换。

## 认证

除了登录和注册接口外，所有API请求都需要在HTTP头部包含授权令牌：

```
Authorization: Bearer {token}
```

### 认证API

#### 用户登录

```
POST /api/auth/login
```

请求体：
```json
{
  "username": "string",
  "password": "string"
}
```

响应：
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "string"
  }
}
```

#### 用户注册

```
POST /api/auth/register
```

请求体：
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "student" // 或 "teacher"
}
```

响应：
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "role": "string"
}
```

## 用户管理

### 获取用户列表 (仅管理员)

```
GET /api/users
```

查询参数：
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "username": "string",
    "email": "string",
    "role": "string"
  }
]
```

### 获取用户详情

```
GET /api/users/{user_id}
```

响应：
```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "role": "string"
}
```

## 班级管理

### 创建班级

```
POST /api/classes
```

请求体：
```json
{
  "name": "string",
  "description": "string"
}
```

响应：
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "created_by": "integer"
}
```

### 获取班级列表

```
GET /api/classes
```

查询参数：
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "name": "string",
    "description": "string",
    "created_at": "datetime",
    "created_by": "integer"
  }
]
```

### 添加班级成员

```
POST /api/classes/{class_id}/members
```

请求体：
```json
{
  "user_id": "integer",
  "role": "student" // 或 "teacher"
}
```

响应：
```json
{
  "id": "integer",
  "class_id": "integer",
  "user_id": "integer",
  "role": "string",
  "joined_at": "datetime"
}
```

## 课程管理

### 创建课程

```
POST /api/courses
```

请求体：
```json
{
  "name": "string",
  "description": "string",
  "class_id": "integer"
}
```

响应：
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "class_id": "integer",
  "teacher_id": "integer",
  "status": "active",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 获取班级的课程列表

```
GET /api/classes/{class_id}/courses
```

查询参数：
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "name": "string",
    "description": "string",
    "class_id": "integer",
    "teacher_id": "integer",
    "status": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

## 作业管理

### 创建作业

```
POST /api/assignments
```

请求体：
```json
{
  "title": "string",
  "description": "string",
  "course_id": "integer",
  "due_date": "datetime",
  "total_points": "integer"
}
```

响应：
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "course_id": "integer",
  "due_date": "datetime",
  "total_points": "integer",
  "attachment_url": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### 获取课程的作业列表

```
GET /api/courses/{course_id}/assignments
```

查询参数：
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "course_id": "integer",
    "due_date": "datetime",
    "total_points": "integer",
    "attachment_url": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

## 作业提交

### 提交作业

```
POST /api/submissions
```

请求体 (multipart/form-data):
```
{
  "assignment_id": "integer",
  "comments": "string",
  "file": [file]
}
```

响应：
```json
{
  "id": "integer",
  "assignment_id": "integer",
  "student_id": "integer",
  "submission_time": "datetime",
  "file_url": "string",
  "status": "submitted",
  "comments": "string"
}
```

### 获取作业的提交列表

```
GET /api/assignments/{assignment_id}/submissions
```

查询参数：
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "assignment_id": "integer",
    "student_id": "integer",
    "student_name": "string",
    "submission_time": "datetime",
    "file_url": "string",
    "status": "string",
    "comments": "string"
  }
]
```

## 作业批改

### 批改作业

```
POST /api/gradings
```

请求体：
```json
{
  "submission_id": "integer",
  "score": "number",
  "feedback": "string"
}
```

响应：
```json
{
  "id": "integer",
  "submission_id": "integer",
  "teacher_id": "integer",
  "score": "number",
  "feedback": "string",
  "graded_at": "datetime",
  "updated_at": "datetime"
}
```

### 获取提交的批改

```
GET /api/submissions/{submission_id}/gradings
```

响应：
```json
{
  "id": "integer",
  "submission_id": "integer",
  "teacher_id": "integer",
  "teacher_name": "string",
  "score": "number",
  "feedback": "string",
  "graded_at": "datetime",
  "updated_at": "datetime"
}
```

## 通知管理

### 获取用户的通知列表

```
GET /api/notifications
```

查询参数：
- `is_read`: 是否已读 (可选)
- `skip`: 跳过的记录数 (默认: 0)
- `limit`: 返回的最大记录数 (默认: 100)

响应：
```json
[
  {
    "id": "integer",
    "user_id": "integer",
    "title": "string",
    "content": "string",
    "type": "string",
    "is_read": "boolean",
    "created_at": "datetime"
  }
]
```

### 标记通知为已读

```
PUT /api/notifications/{notification_id}/read
```

响应：
```json
{
  "id": "integer",
  "user_id": "integer",
  "title": "string",
  "content": "string",
  "type": "string",
  "is_read": true,
  "created_at": "datetime"
}
```

## 统计分析

### 获取作业统计

```
GET /api/statistics/assignments/{assignment_id}
```

响应：
```json
{
  "assignment_id": "integer",
  "assignment_title": "string",
  "total_submissions": "integer",
  "graded_submissions": "integer",
  "average_score": "number",
  "highest_score": "number",
  "lowest_score": "number",
  "score_distribution": {
    "ranges": ["0-10", "11-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91-100"],
    "counts": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  }
}
```

### 获取课程统计

```
GET /api/statistics/courses/{course_id}
```

响应：
```json
{
  "course_id": "integer",
  "course_name": "string",
  "total_assignments": "integer",
  "total_students": "integer",
  "assignment_completion_rate": "number",
  "average_course_score": "number"
}
```

## 状态码

- 200: 成功
- 201: 已创建
- 400: 错误请求
- 401: 未授权
- 403: 禁止访问
- 404: 资源未找到
- 422: 无法处理实体
- 500: 服务器内部错误

## 错误响应

当发生错误时，响应将包含错误信息：

```json
{
  "detail": "错误消息"
}
```

对于验证错误：

```json
{
  "detail": [
    {
      "loc": ["路径", "字段"],
      "msg": "错误描述",
      "type": "错误类型"
    }
  ]
}
``` 