from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..db import models
from ..schemas.task import ReturnTask, TaskCreate, TaskEdit
from .utils import to_dict


def get_task_by_id(db: Session, task_id: int) -> Optional[ReturnTask]:
    result = db.query(models.Task).filter(models.Task.id == task_id).one_or_none()
    return None if result is None else ReturnTask.parse_obj(to_dict(result))


def get_task_by_name(db: Session, name: str) -> Optional[ReturnTask]:
    result = db.query(models.Task).filter(models.Task.name == name).one_or_none()
    return None if result is None else ReturnTask.parse_obj(to_dict(result))


def delete_task_by_id(db: Session, task_id: int) -> Optional[ReturnTask]:
    result = db.query(models.Task).filter(models.Task.id == task_id).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnTask.parse_obj(to_dict(result))


def delete_task_by_name(db: Session, name: str) -> Optional[ReturnTask]:
    result = db.query(models.Task).filter(models.Task.name == name).one_or_none()
    if result:
        db.delete(result)
        db.commit()
        return ReturnTask.parse_obj(to_dict(result))


def get_all_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[ReturnTask]:
    result = db.query(models.Task).offset(skip).limit(limit).all()
    return [ReturnTask.parse_obj(to_dict(obj)) for obj in result]


def create_task(db: Session, new_task: TaskCreate, manager_id: int) -> ReturnTask:
    requirement_id = get_or_create_requirement(db, new_task.requirement_link)
    db_task = models.Task(
        name=new_task.name,
        description=new_task.description,
        state_id=new_task.state_id,
        manager_id=manager_id,
        assignee_id=new_task.assignee_id,
        project_id=new_task.project_id,
        requirement_id=requirement_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return ReturnTask.parse_obj(to_dict(db_task))


def edit_task(db: Session, new_task: TaskEdit, task_id: int) -> Optional[ReturnTask]:
    result = db.query(models.Task).filter(models.Task.id == task_id).one_or_none()
    if result is None:
        return None

    requirement_id = get_or_create_requirement(db, new_task.requirement_link)
    result.name = new_task.name
    result.description = new_task.description
    result.state_id = new_task.state_id
    result.assignee_id = new_task.assignee_id
    result.project_id = new_task.project_id
    result.finished_at = new_task.finished_at
    result.requirement_id = requirement_id

    db.add(result)
    db.commit()
    db.refresh(result)
    return ReturnTask.parse_obj(to_dict(result))


def get_or_create_requirement(db: Session, requirement_link: str) -> int:
    result = (
        db.query(models.Requirement)
        .filter(models.Requirement.link == requirement_link)
        .one_or_none()
    )
    if result is not None:
        return result.id
    db_requirement = models.Requirement(link=requirement_link)
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement.id
