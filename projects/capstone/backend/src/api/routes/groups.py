from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from typing import List
from pydantic import BaseModel
from ...database import get_db
from contextlib import asynccontextmanager
from ...models.group import WordGroup
from ...models.word import Word, word_group_map
from ...models.study_session import StudySession
from ...schemas.group import (
    WordGroupCreate,
    WordGroupUpdate,
    WordGroupResponse,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/groups", tags=["groups"])


class BulkWordAdd(BaseModel):
    word_ids: List[int]


@router.get("")
async def get_groups(
    group_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Get all groups with optional type filter"""
    try:
        async with db_cm as db:
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
async def get_group(
    group_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    async with db_cm as db:
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
    db_cm: asynccontextmanager = Depends(get_db),
):
    async with db_cm as db:
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
    db_cm: asynccontextmanager = Depends(get_db),
):
    async with db_cm as db:
        query = (
            select(StudySession)
            .filter(StudySession.group_id == group_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()


# @router.post("", response_model=WordGroupResponse)
# async def create_group(
#     group: WordGroupCreate, db: AsyncSession = Depends(get_db)
# ):
#     db_group = WordGroup(**group.dict())
#     db.add(db_group)
#     await db.commit()
#     await db.refresh(db_group)
#     return db_group


@router.post("", response_model=WordGroupResponse, status_code=201)
async def create_group(
    group: WordGroupCreate, db_cm: asynccontextmanager = Depends(get_db)
):
    """Create a new group"""
    logger.info(f"Creating group: {group.dict()}")
    try:
        async with db_cm as db:
            db_group = WordGroup(**group.dict())
            db.add(db_group)
            await db.commit()
            await db.refresh(db_group)
            logger.info(f"Group created successfully: {db_group.id}")
            return db_group
    except Exception as e:
        logger.exception(
            f"Error creating group: {e}"
        )  # Log the full traceback
        await db.rollback()  # Rollback on error
        raise HTTPException(status_code=500, detail="Failed to create group")


@router.put("/{group_id}", response_model=WordGroupResponse)
async def update_group(
    group_id: int,
    group: WordGroupUpdate,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Update a group's details"""
    async with db_cm as db:
        result = await db.execute(
            select(WordGroup).filter(WordGroup.id == group_id)
        )
        db_group = result.scalar_one_or_none()
        if not db_group:
            raise HTTPException(status_code=404, detail="Group not found")

        for key, value in group.dict(exclude_unset=True).items():
            setattr(db_group, key, value)
        try:
            await db.commit()
            await db.refresh(db_group)
            return db_group
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error updating group {group_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to update group"
            )


@router.post("/{group_id}/add-word/{word_id}")
async def add_word_to_group(
    group_id: int, word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Add a word to a group"""
    async with db_cm as db:
        # Verify both exist
        group_res = await db.execute(
            select(WordGroup).filter(WordGroup.id == group_id)
        )
        word_res = await db.execute(select(Word).filter(Word.id == word_id))
        group = group_res.scalar_one_or_none()
        word = word_res.scalar_one_or_none()

        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        if not word:
            raise HTTPException(status_code=404, detail="Word not found")

        # Add association
        try:
            stmt = word_group_map.insert().values(
                word_id=word_id, group_id=group_id
            )
            await db.execute(stmt)
            await db.commit()
            return {"message": "Word added to group successfully"}
        except (
            Exception
        ) as e:  # Catch potential integrity errors if relationship exists
            await db.rollback()
            logger.exception(
                f"Error adding word {word_id} to group {group_id}: {e}"
            )
            # Check if it's a unique constraint violation (specific error
            # depends on DB)
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(
                    status_code=409, detail="Word already in group"
                )
            raise HTTPException(
                status_code=500, detail="Failed to add word to group"
            )


@router.post("/{group_id}/words", status_code=201)
async def add_words_to_group(
    group_id: int,
    words: BulkWordAdd,
    db_cm: asynccontextmanager = Depends(get_db),
):
    """Add multiple words to a group"""
    async with db_cm as db:
        # Verify group exists
        group_res = await db.execute(
            select(WordGroup).filter(WordGroup.id == group_id)
        )
        if not group_res.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Group not found")

        # Verify all words exist
        word_count_res = await db.execute(
            select(func.count(Word.id)).filter(Word.id.in_(words.word_ids))
        )
        if word_count_res.scalar() != len(words.word_ids):
            # Find which words are missing (optional, but helpful for
            # debugging)
            existing_words_res = await db.execute(
                select(Word.id).filter(Word.id.in_(words.word_ids))
            )
            existing_word_ids = {row[0] for row in existing_words_res}
            missing_ids = set(words.word_ids) - existing_word_ids
            logger.warning(f"Words not found: {missing_ids}")
            detail_msg = f"One or more words not found: {list(missing_ids)}"
            raise HTTPException(
                status_code=404,
                detail=detail_msg,
            )

        # Add all associations
        values = [
            {"word_id": word_id, "group_id": group_id}
            for word_id in words.word_ids
        ]
        try:
            # Consider checking for existing associations first if duplicates
            # should be ignored silently Or handle potential integrity errors
            # if duplicates should raise an error
            await db.execute(
                word_group_map.insert().prefix_with("OR IGNORE"), values
            )  # Use OR IGNORE for SQLite to skip duplicates
            await db.commit()
            # Get actual count added if needed (more complex query)
            # Could query word_group_map count before/after or use returning
            # clause if DB supports
            return {
                "message": (
                    f"Attempted to add {len(words.word_ids)} words to group "
                    f"{group_id}. Duplicates ignored."
                )
            }
        except Exception as e:
            await db.rollback()
            logger.exception(
                f"Error bulk adding words to group {group_id}: {e}"
            )
            raise HTTPException(
                status_code=500, detail="Failed to add words to group"
            )


@router.delete("/{group_id}/remove-word/{word_id}")
async def remove_word_from_group(
    group_id: int, word_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Remove a word from a group"""
    async with db_cm as db:
        stmt = word_group_map.delete().where(
            word_group_map.c.word_id == word_id,
            word_group_map.c.group_id == group_id,
        )
        try:
            result = await db.execute(stmt)
            await db.commit()
            if result.rowcount == 0:
                # Check if group or word exists to give a more specific error
                group_exists = (
                    await db.execute(
                        select(WordGroup.id).filter(WordGroup.id == group_id)
                    )
                ).scalar()
                word_exists = (
                    await db.execute(
                        select(Word.id).filter(Word.id == word_id)
                    )
                ).scalar()
                if not group_exists:
                    raise HTTPException(
                        status_code=404, detail="Group not found"
                    )
                if not word_exists:
                    raise HTTPException(
                        status_code=404, detail="Word not found"
                    )
                # If both exist, the word wasn't in the group
                raise HTTPException(
                    status_code=404, detail="Word not found in group"
                )
            return {"message": "Word removed from group successfully"}
        except Exception as e:
            await db.rollback()
            log_msg = (
                f"Error removing word {word_id} from group {group_id}: {e}"
            )
            logger.exception(log_msg)
            raise HTTPException(
                status_code=500, detail="Failed to remove word from group"
            )


@router.delete("/{group_id}")
async def delete_group(
    group_id: int, db_cm: asynccontextmanager = Depends(get_db)
):
    """Delete a group"""
    async with db_cm as db:
        result = await db.execute(
            select(WordGroup).filter(WordGroup.id == group_id)
        )
        group = result.scalar_one_or_none()
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        try:
            # Note: Depending on cascade rules, related word_group_map entries might be deleted automatically.
            # If not, you might need to delete them manually first.
            await db.delete(group)
            await db.commit()
            return {"message": "Group deleted successfully"}
        except Exception as e:
            await db.rollback()
            logger.exception(f"Error deleting group {group_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to delete group"
            )
