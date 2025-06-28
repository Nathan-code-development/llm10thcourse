#!/usr/bin/env python3
"""
数据库管理脚本
用于初始化数据库、创建示例数据等操作
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.db.session import create_db_and_tables, get_session
from app.models.user import User, UserRole
from app.models.class_model import Class, ClassMember
from app.models.course import Course, CourseStatus
from app.models.assignment import Assignment
from app.core.security import get_password_hash


def init_database():
    """初始化数据库"""
    print("正在创建数据库表...")
    create_db_and_tables()
    print("✅ 数据库表创建完成")


def create_sample_data():
    """创建示例数据"""
    print("正在创建示例数据...")
    
    with get_session() as session:
        # 创建示例老师
        teacher = User(
            username="teacher1",
            email="teacher1@example.com",
            role=UserRole.TEACHER,
            hashed_password=get_password_hash("123456")
        )
        session.add(teacher)
        session.commit()
        session.refresh(teacher)
        
        # 创建示例学生
        student = User(
            username="student1",
            email="student1@example.com",
            role=UserRole.STUDENT,
            hashed_password=get_password_hash("123456")
        )
        session.add(student)
        session.commit()
        session.refresh(student)
        
        # 创建示例班级
        class_ = Class(
            name="Python编程基础",
            description="学习Python编程的基础知识",
            created_by=teacher.id
        )
        session.add(class_)
        session.commit()
        session.refresh(class_)
        
        # 老师加入班级
        teacher_member = ClassMember(
            class_id=class_.id,
            user_id=teacher.id,
            role="teacher"
        )
        session.add(teacher_member)
        
        # 学生加入班级
        student_member = ClassMember(
            class_id=class_.id,
            user_id=student.id,
            role="student"
        )
        session.add(student_member)
        session.commit()
        
        # 创建示例课程
        course = Course(
            name="第一课：Python简介",
            description="了解Python的历史和特点",
            class_id=class_.id,
            teacher_id=teacher.id,
            status=CourseStatus.ACTIVE
        )
        session.add(course)
        session.commit()
        session.refresh(course)
        
        # 创建示例作业
        assignment = Assignment(
            title="作业1：Hello World",
            description="编写你的第一个Python程序",
            course_id=course.id,
            due_date=datetime.utcnow() + timedelta(days=7),
            total_points=100
        )
        session.add(assignment)
        session.commit()
        
    print("✅ 示例数据创建完成")
    print("\n示例账户信息:")
    print("老师账户: teacher1 / 123456")
    print("学生账户: student1 / 123456")


def reset_database():
    """重置数据库"""
    print("⚠️  警告：这将删除所有数据！")
    confirm = input("确定要继续吗？(输入 'yes' 确认): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    # 删除数据库文件
    db_path = Path("homework_system.db")
    if db_path.exists():
        db_path.unlink()
        print("✅ 数据库文件已删除")
    
    # 重新创建数据库
    init_database()
    create_sample_data()


def main():
    """主函数"""
    print("=== 作业管理系统数据库管理工具 ===")
    print("1. 初始化数据库")
    print("2. 创建示例数据")
    print("3. 重置数据库")
    print("4. 完整初始化（初始化+示例数据）")
    print("0. 退出")
    
    choice = input("\n请选择操作 (0-4): ")
    
    if choice == "1":
        init_database()
    elif choice == "2":
        create_sample_data()
    elif choice == "3":
        reset_database()
    elif choice == "4":
        init_database()
        create_sample_data()
    elif choice == "0":
        print("再见！")
    else:
        print("无效选择")


if __name__ == "__main__":
    main() 