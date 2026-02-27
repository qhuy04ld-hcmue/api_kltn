from fastapi import APIRouter
from app.services.postgres_service import update_record

router = APIRouter(prefix="/api/postgres", tags=["Postgres"])

@router.put("/{table}/{record_id}")
async def update_data(table: str, record_id: str, payload: dict):
    result = update_record(table, record_id, payload)
    return {"status": "updated", "data": result}