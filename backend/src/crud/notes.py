from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Notes
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.token import Status
from src.schemas.users import UserOutSchema


async def create_note(note: NoteInSchema, current_user: UserOutSchema):
    note_dict = note.dict(exclude_unset=True)

    note_dict['author_id'] = current_user.id

    note_obj = await Notes.create(**note_dict)
    return await NoteOutSchema.from_tortoise_orm(note_obj)


async def read_notes():
    return await NoteOutSchema.from_queryset(Notes.all())


async def read_note(note_id: int):
    try:
        return await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")


async def update_note(note_id: int, note: UpdateNote, current_user: UserOutSchema):
    try:
        db_note = await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")

    if db_note.author.id != current_user.id:
        raise HTTPException(status_code=403, detail=f"Not authorized to update note {note_id}")

    await Notes.filter(id=note_id).update(**note.model_dump(exclude_unset=True))
    return await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))


async def delete_note(note_id: int, current_user: UserOutSchema):
    try:
        db_note = await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")

    if db_note.author.id != current_user.id:
        raise HTTPException(status_code=403, detail=f"Not authorized to delete note {note_id}")
    await Notes.filter(id=note_id).delete()

    return Status(message=f"Deleted note {note_id}")
