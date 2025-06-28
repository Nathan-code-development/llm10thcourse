from sqlmodel import Session, select

from app.models.class_model import ClassMember
from app.models.course import Course
from app.models.notification import Notification, NotificationType
from app.models.submission import Submission
from app.models.user import User


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    notification_type: NotificationType,
) -> Notification:
    """
    创建通知
    
    Args:
        db: 数据库会话
        user_id: 接收通知的用户ID
        title: 通知标题
        content: 通知内容
        notification_type: 通知类型
        
    Returns:
        创建的通知
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        content=content,
        type=notification_type,
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def notify_assignment_created(
    db: Session,
    course_id: int,
    assignment_id: int,
    assignment_title: str,
) -> None:
    """
    通知作业创建
    
    Args:
        db: 数据库会话
        course_id: 课程ID
        assignment_id: 作业ID
        assignment_title: 作业标题
    """
    # 获取课程
    course = db.get(Course, course_id)
    if not course:
        return
    
    # 获取班级学生
    students = db.exec(
        select(User)
        .join(ClassMember, User.id == ClassMember.user_id)
        .where(
            ClassMember.class_id == course.class_id,
            ClassMember.role == "student",
        )
    ).all()
    
    # 发送通知给每个学生
    for student in students:
        create_notification(
            db=db,
            user_id=student.id,
            title=f"新作业: {assignment_title}",
            content=f"在课程 '{course.name}' 中发布了新作业 '{assignment_title}'。请查看详情并及时完成。",
            notification_type=NotificationType.ASSIGNMENT,
        )


def notify_grading_completed(
    db: Session,
    submission_id: int,
    assignment_title: str,
    score: float,
) -> None:
    """
    通知作业批改完成
    
    Args:
        db: 数据库会话
        submission_id: 提交ID
        assignment_title: 作业标题
        score: 得分
    """
    # 获取提交记录
    submission = db.get(Submission, submission_id)
    if not submission:
        return
    
    # 发送通知给学生
    create_notification(
        db=db,
        user_id=submission.student_id,
        title=f"作业已批改: {assignment_title}",
        content=f"你提交的作业 '{assignment_title}' 已被批改，得分: {score}。请查看详情获取反馈。",
        notification_type=NotificationType.FEEDBACK,
    )


def notify_assignment_due_soon(
    db: Session,
    assignment_id: int,
    assignment_title: str,
    course_id: int,
    course_name: str,
    days_remaining: int,
) -> None:
    """
    通知作业即将截止
    
    Args:
        db: 数据库会话
        assignment_id: 作业ID
        assignment_title: 作业标题
        course_id: 课程ID
        course_name: 课程名称
        days_remaining: 剩余天数
    """
    # 获取已提交的学生ID
    submitted_student_ids = db.exec(
        select(Submission.student_id).where(
            Submission.assignment_id == assignment_id
        )
    ).all()
    
    # 获取未提交的学生
    students = db.exec(
        select(User)
        .join(ClassMember, User.id == ClassMember.user_id)
        .join(Course, Course.class_id == ClassMember.class_id)
        .where(
            Course.id == course_id,
            ClassMember.role == "student",
            ~User.id.in_(submitted_student_ids),
        )
    ).all()
    
    # 发送通知给每个未提交作业的学生
    for student in students:
        create_notification(
            db=db,
            user_id=student.id,
            title=f"作业即将截止: {assignment_title}",
            content=f"课程 '{course_name}' 中的作业 '{assignment_title}' 将在 {days_remaining} 天后截止。请及时完成并提交。",
            notification_type=NotificationType.REMINDER,
        )


def mark_notifications_as_read(db: Session, user_id: int, notification_ids: list[int] = None) -> int:
    """
    标记通知为已读
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        notification_ids: 通知ID列表，为None时标记所有通知
        
    Returns:
        标记为已读的通知数量
    """
    # 构建查询
    query = select(Notification).where(
        Notification.user_id == user_id,
        Notification.is_read == False,
    )
    
    if notification_ids:
        query = query.where(Notification.id.in_(notification_ids))
    
    # 获取通知
    notifications = db.exec(query).all()
    
    # 标记为已读
    for notification in notifications:
        notification.is_read = True
        db.add(notification)
    
    db.commit()
    
    return len(notifications) 