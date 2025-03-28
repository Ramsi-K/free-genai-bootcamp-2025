from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from ...database import get_db
from ...models.group import Group
from ...models.word import Word
from ...models.study_session import StudySession
from ...schemas.group import GroupCreate, Group as GroupSchema

router = APIRouter()


@router.get("")
async def get_groups(
    group_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """Get all groups with optional type filter"""
    try:
        print(f"API: Fetching groups with type: {group_type}")
        query = select(Group)
        if group_type:
            query = query.filter(Group.group_type == group_type)

        result = await db.execute(query)
        groups = result.scalars().all()

        print(f"API: Found {len(groups)} groups")
        for group in groups:
            print(
                f"- {group.name} ({group.group_type}): {group.words_count} words"
            )

        return groups
    except Exception as e:
        print(f"API Error in get_groups: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )


@router.get("/{group_id}", response_model=GroupSchema)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Group).filter(Group.id == group_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


@router.get("/{group_id}/words")
async def get_group_words(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Word)
        .join(Word.groups)
        .filter(Group.id == group_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{group_id}/study_sessions")
async def get_group_study_sessions(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(StudySession)
        .filter(StudySession.group_id == group_id)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=GroupSchema)
async def create_group(group: GroupCreate, db: AsyncSession = Depends(get_db)):
    db_group = Group(**group.dict())
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group
