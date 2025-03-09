from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from src.database.models import Notes
from src.schemas.notes import NoteOutSchema
from src.schemas.token import Status


async def create_note(note, current_user):
    note_dict = note.dict(exclude_unset=True)

    note_dict['author.id'] = current_user.id

    note_obj = await Notes.create(**note_dict)
    return await NoteOutSchema.from_tortoise_orm(note_obj)


async def read_notes():
    return await NoteOutSchema.from_queryset(Notes.all())


async def read_note(note_id):
    return await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))


async def update_note(note_id, note, current_user):
    try:
        db_note = await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")

    if db_note.author.id != current_user.id:
        raise HTTPException(status_code=403, detail=f"Not authorized to update note {note_id}")

    await Notes.filter(id=note_id).update(**note.dict(exclude_unset=True))
    return await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))


async def delete_note(note_id, current_user):
    try:
        db_note = await NoteOutSchema.from_queryset_single(Notes.get(id=note_id))
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")

    if db_note.author.id != current_user.id:
        raise HTTPException(status_code=403, detail=f"Not authorized to delete note {note_id}")
    await Notes.filter(id=note_id).delete()

    return Status(message=f"Deleted note {note_id}")
