from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel
from ...database import get_db
from ...models.group import WordGroup
from ...models.word import Word, word_group_map
from ...models.study_session import StudySession
from ...schemas.word_group import (
    WordGroupCreate,
    WordGroupUpdate,
    WordGroupResponse,
)

router = APIRouter(prefix="/groups", tags=["groups"])


class BulkWordAdd(BaseModel):
    word_ids: List[int]


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
        query = select(WordGroup)
        if group_type:
            query = query.filter(WordGroup.group_type == group_type)

        result = await db.execute(query)
        groups = result.scalars().all()

        print(f"API: Found {len(groups)} groups")
        for group in groups:
            print(
                f"- {group.name} ({group.group_type}): "
                f"{len(group.words)} words"
            )

        return groups
    except Exception as e:
        print(f"API Error in get_groups: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )


@router.get("/{group_id}", response_model=WordGroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    query = select(WordGroup).filter(WordGroup.id == group_id)
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
        .filter(WordGroup.id == group_id)
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


@router.post("", response_model=WordGroupResponse)
async def create_group(
    group: WordGroupCreate, db: AsyncSession = Depends(get_db)
):
    db_group = WordGroup(**group.dict())
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group


@router.put("/{group_id}", response_model=WordGroupResponse)
async def update_group(
    group_id: int, group: WordGroupUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a group's details"""
    result = await db.execute(
        select(WordGroup).filter(WordGroup.id == group_id)
    )
    db_group = result.scalar_one_or_none()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    for key, value in group.dict(exclude_unset=True).items():
        setattr(db_group, key, value)
    await db.commit()
    await db.refresh(db_group)
    return db_group


@router.post("/{group_id}/add-word/{word_id}")
async def add_word_to_group(
    group_id: int, word_id: int, db: AsyncSession = Depends(get_db)
):
    """Add a word to a group"""
    # Verify both exist
    group = await db.execute(
        select(WordGroup).filter(WordGroup.id == group_id)
    )
    word = await db.execute(select(Word).filter(Word.id == word_id))

    if not group.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Group not found")
    if not word.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Word not found")

    # Add association
    stmt = word_group_map.insert().values(word_id=word_id, group_id=group_id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Word added to group successfully"}


@router.post("/{group_id}/words", status_code=201)
async def add_words_to_group(
    group_id: int, words: BulkWordAdd, db: AsyncSession = Depends(get_db)
):
    """Add multiple words to a group"""
    # Verify group exists
    group = await db.execute(
        select(WordGroup).filter(WordGroup.id == group_id)
    )
    if not group.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Group not found")

    # Verify all words exist
    word_count = await db.execute(
        select(func.count(Word.id)).filter(Word.id.in_(words.word_ids))
    )
    if word_count.scalar() != len(words.word_ids):
        raise HTTPException(
            status_code=404, detail="One or more words not found"
        )

    # Add all associations
    values = [
        {"word_id": word_id, "group_id": group_id}
        for word_id in words.word_ids
    ]
    await db.execute(word_group_map.insert(), values)
    await db.commit()

    return {
        "message": f"Added {len(words.word_ids)} words to group {group_id}"
    }


@router.delete("/{group_id}/remove-word/{word_id}")
async def remove_word_from_group(
    group_id: int, word_id: int, db: AsyncSession = Depends(get_db)
):
    """Remove a word from a group"""
    stmt = word_group_map.delete().where(
        word_group_map.c.word_id == word_id,
        word_group_map.c.group_id == group_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Word not found in group")
    return {"message": "Word removed from group successfully"}


@router.delete("/{group_id}")
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a group"""
    result = await db.execute(
        select(WordGroup).filter(WordGroup.id == group_id)
    )
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    await db.delete(group)
    await db.commit()
    return {"message": "Group deleted successfully"}
