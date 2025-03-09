from typing import List

from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import DoesNotExist

from src.auth.jwthandler import read_current_user
import src.crud.notes as notes_crud
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote
from src.schemas.token import Status

router = APIRouter()


@router.post(path='/notes', response_model=NoteOutSchema, dependencies=[Depends(read_current_user)])
async def create_note(note: NoteInSchema, current_user=Depends(read_current_user)):
    return await notes_crud.create_note(note, current_user)


@router.get(path='/notes', response_model=List[NoteOutSchema], dependencies=[Depends(read_current_user)])
async def read_notes():
    return await notes_crud.read_notes()


@router.get(path='/note/{note-id}', response_model=NoteOutSchema, dependencies=[Depends(read_current_user)])
async def read_note(note_id: int):
    try:
        return await notes_crud.read_note(note_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Note {note_id} not found")


@router.patch(path='/note/{note-id}', response_model=NoteOutSchema, responses={404: {'model': HTTPException}},
              dependencies=[Depends(read_current_user)])
async def update_note(note_id: int, note: UpdateNote, current_user=Depends(read_current_user)):
    return await notes_crud.update_note(note_id, note, current_user)


@router.delete(path='/note/{note-id}', response_model=Status, responses={404: {'model': HTTPException}},
               dependencies=[Depends(read_current_user)])
async def delete_note(note_id: int, current_user=Depends(read_current_user)):
    return await notes_crud.delete_note(note_id, current_user)
