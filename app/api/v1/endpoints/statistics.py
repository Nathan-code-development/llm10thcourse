from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.api.deps import get_current_active_user, get_current_teacher_user, get_db
from app.models.assignment import Assignment
from app.models.class_model import Class, ClassMember
from app.models.course import Course
from app.models.grading import Grading
from app.models.submission import Submission
from app.models.user import User

router = APIRouter()


@router.get("/assignments/{assignment_id}")
def get_assignment_statistics(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    获取作业统计信息(仅教师)
    """
    # 查询作业
    assignment = db.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="作业不存在",
        )
    
    # 获取课程信息
    course = db.get(Course, assignment.course_id)
    
    # 权限检查：只有课程教师和管理员可以查看作业统计
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此作业统计",
        )
    
    # 获取班级成员数量(学生)
    class_students_count = db.exec(
        select(func.count(ClassMember.id)).where(
            ClassMember.class_id == course.class_id,
            ClassMember.role == "student",
        )
    ).one()
    
    # 获取提交数量
    total_submissions = db.exec(
        select(func.count(Submission.id)).where(
            Submission.assignment_id == assignment_id,
        )
    ).one()
    
    # 获取已批改数量
    graded_submissions = db.exec(
        select(func.count(Grading.id)).where(
            Grading.submission.has(assignment_id=assignment_id),
        )
    ).one()
    
    # 获取分数信息
    gradings = db.exec(
        select(Grading).join(Submission).where(
            Submission.assignment_id == assignment_id,
        )
    ).all()
    
    scores = [g.score for g in gradings] if gradings else []
    
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    # 分数分布
    ranges = ["0-10", "11-20", "21-30", "31-40", "41-50", 
              "51-60", "61-70", "71-80", "81-90", "91-100"]
    
    distribution = [0] * len(ranges)
    for score in scores:
        index = min(int(score / 10), 9)  # 将分数归入对应的区间
        distribution[index] += 1
    
    # 构建统计结果
    result = {
        "assignment_id": assignment_id,
        "assignment_title": assignment.title,
        "total_students": class_students_count,
        "total_submissions": total_submissions,
        "submission_rate": total_submissions / class_students_count if class_students_count > 0 else 0,
        "graded_submissions": graded_submissions,
        "grading_rate": graded_submissions / total_submissions if total_submissions > 0 else 0,
        "average_score": avg_score,
        "highest_score": max_score,
        "lowest_score": min_score,
        "score_distribution": {
            "ranges": ranges,
            "counts": distribution,
        },
    }
    
    return result


@router.get("/courses/{course_id}")
def get_course_statistics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    获取课程统计信息(仅教师)
    """
    # 查询课程
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="课程不存在",
        )
    
    # 权限检查：只有课程教师和管理员可以查看课程统计
    if current_user.role != "admin" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此课程统计",
        )
    
    # 获取学生数量
    total_students = db.exec(
        select(func.count(ClassMember.id)).where(
            ClassMember.class_id == course.class_id,
            ClassMember.role == "student",
        )
    ).one()
    
    # 获取作业数量
    total_assignments = db.exec(
        select(func.count(Assignment.id)).where(
            Assignment.course_id == course_id,
        )
    ).one()
    
    # 获取每个作业的提交情况
    assignments = db.exec(
        select(Assignment).where(Assignment.course_id == course_id)
    ).all()
    
    assignment_stats = []
    total_submission_rate = 0
    total_avg_score = 0
    
    for assignment in assignments:
        # 获取提交数量
        submissions_count = db.exec(
            select(func.count(Submission.id)).where(
                Submission.assignment_id == assignment.id,
            )
        ).one()
        
        submission_rate = submissions_count / total_students if total_students > 0 else 0
        
        # 获取分数信息
        gradings = db.exec(
            select(Grading).join(Submission).where(
                Submission.assignment_id == assignment.id,
            )
        ).all()
        
        scores = [g.score for g in gradings] if gradings else []
        avg_score = sum(scores) / len(scores) if scores else 0
        
        assignment_stats.append({
            "assignment_id": assignment.id,
            "title": assignment.title,
            "submissions_count": submissions_count,
            "submission_rate": submission_rate,
            "average_score": avg_score,
        })
        
        total_submission_rate += submission_rate
        total_avg_score += avg_score
    
    # 计算平均值
    avg_submission_rate = total_submission_rate / total_assignments if total_assignments > 0 else 0
    avg_course_score = total_avg_score / total_assignments if total_assignments > 0 else 0
    
    # 构建统计结果
    result = {
        "course_id": course_id,
        "course_name": course.name,
        "total_students": total_students,
        "total_assignments": total_assignments,
        "average_submission_rate": avg_submission_rate,
        "average_course_score": avg_course_score,
        "assignments": assignment_stats,
    }
    
    return result


@router.get("/users/{user_id}")
def get_user_statistics(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取用户统计信息
    """
    # 权限检查：只能查看自己的统计或者是管理员/教师
    if current_user.id != user_id and current_user.role == "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看此用户统计",
        )
    
    # 查询用户
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    
    # 如果是学生，获取提交情况
    if user.role == "student":
        # 获取用户所在的班级
        class_members = db.exec(
            select(ClassMember).where(ClassMember.user_id == user_id)
        ).all()
        class_ids = [cm.class_id for cm in class_members]
        
        # 获取用户所在班级的课程
        courses = db.exec(
            select(Course).where(Course.class_id.in_(class_ids))
        ).all()
        
        course_stats = []
        
        for course in courses:
            # 获取课程的作业
            assignments = db.exec(
                select(Assignment).where(Assignment.course_id == course.id)
            ).all()
            
            assignment_stats = []
            total_score = 0
            total_graded = 0
            
            for assignment in assignments:
                # 查询提交记录
                submission = db.exec(
                    select(Submission).where(
                        Submission.assignment_id == assignment.id,
                        Submission.student_id == user_id,
                    )
                ).first()
                
                # 查询批改记录
                grading = None
                if submission:
                    grading = db.exec(
                        select(Grading).where(
                            Grading.submission_id == submission.id,
                        )
                    ).first()
                
                # 统计信息
                status = "not_submitted"
                score = None
                
                if submission:
                    status = "submitted"
                    if grading:
                        status = "graded"
                        score = grading.score
                        total_score += score
                        total_graded += 1
                
                assignment_stats.append({
                    "assignment_id": assignment.id,
                    "title": assignment.title,
                    "status": status,
                    "score": score,
                    "due_date": assignment.due_date.isoformat(),
                })
            
            # 计算平均分
            avg_score = total_score / total_graded if total_graded > 0 else None
            
            course_stats.append({
                "course_id": course.id,
                "course_name": course.name,
                "total_assignments": len(assignments),
                "completed_assignments": len([a for a in assignment_stats if a["status"] != "not_submitted"]),
                "graded_assignments": total_graded,
                "average_score": avg_score,
                "assignments": assignment_stats,
            })
        
        result = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
            "courses": course_stats,
        }
    
    # 如果是教师，获取教授课程情况
    elif user.role == "teacher":
        # 获取教师的课程
        courses = db.exec(
            select(Course).where(Course.teacher_id == user_id)
        ).all()
        
        course_stats = []
        
        for course in courses:
            # 获取课程的作业
            assignments_count = db.exec(
                select(func.count(Assignment.id)).where(
                    Assignment.course_id == course.id,
                )
            ).one()
            
            # 获取学生数量
            students_count = db.exec(
                select(func.count(ClassMember.id)).where(
                    ClassMember.class_id == course.class_id,
                    ClassMember.role == "student",
                )
            ).one()
            
            course_stats.append({
                "course_id": course.id,
                "course_name": course.name,
                "total_assignments": assignments_count,
                "total_students": students_count,
            })
        
        result = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
            "total_courses": len(courses),
            "courses": course_stats,
        }
    
    # 如果是管理员，获取系统概览
    else:
        # 获取用户数量
        total_users = db.exec(
            select(func.count(User.id))
        ).one()
        
        # 获取班级数量
        total_classes = db.exec(
            select(func.count(Class.id))
        ).one()
        
        # 获取课程数量
        total_courses = db.exec(
            select(func.count(Course.id))
        ).one()
        
        # 获取作业数量
        total_assignments = db.exec(
            select(func.count(Assignment.id))
        ).one()
        
        result = {
            "user_id": user_id,
            "username": user.username,
            "role": user.role,
            "total_users": total_users,
            "total_classes": total_classes,
            "total_courses": total_courses,
            "total_assignments": total_assignments,
        }
    
    return result


@router.get("/classes/{class_id}")
def get_class_statistics(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher_user),
) -> Any:
    """
    获取班级统计信息(仅教师)
    """
    # 查询班级
    class_ = db.get(Class, class_id)
    if not class_:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="班级不存在",
        )
    
    # 权限检查：只有班级教师和管理员可以查看班级统计
    if current_user.role != "admin":
        is_teacher = db.exec(
            select(ClassMember).where(
                ClassMember.class_id == class_id,
                ClassMember.user_id == current_user.id,
                ClassMember.role == "teacher",
            )
        ).first()
        if not is_teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看此班级统计",
            )
    
    # 获取班级成员
    students = db.exec(
        select(User)
        .join(ClassMember, User.id == ClassMember.user_id)
        .where(
            ClassMember.class_id == class_id,
            ClassMember.role == "student",
        )
    ).all()
    
    # 获取班级课程
    courses = db.exec(
        select(Course).where(Course.class_id == class_id)
    ).all()
    
    # 统计每个学生的情况
    student_stats = []
    
    for student in students:
        # 获取学生提交数
        submissions_count = db.exec(
            select(func.count(Submission.id)).where(
                Submission.student_id == student.id
            )
        ).one()
        
        # 获取学生批改数
        gradings = db.exec(
            select(Grading)
            .join(Submission, Grading.submission_id == Submission.id)
            .where(
                Submission.student_id == student.id
            )
        ).all()
        
        # 计算平均分
        scores = [g.score for g in gradings]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        student_stats.append({
            "student_id": student.id,
            "username": student.username,
            "email": student.email,
            "total_submissions": submissions_count,
            "graded_submissions": len(gradings),
            "average_score": avg_score,
        })
    
    # 统计每个课程的情况
    course_stats = []
    
    for course in courses:
        # 获取课程作业数
        assignments_count = db.exec(
            select(func.count(Assignment.id)).where(
                Assignment.course_id == course.id
            )
        ).one()
        
        course_stats.append({
            "course_id": course.id,
            "course_name": course.name,
            "teacher_id": course.teacher_id,
            "total_assignments": assignments_count,
        })
    
    # 构建统计结果
    result = {
        "class_id": class_id,
        "class_name": class_.name,
        "total_students": len(students),
        "total_courses": len(courses),
        "students": student_stats,
        "courses": course_stats,
    }
    
    return result 