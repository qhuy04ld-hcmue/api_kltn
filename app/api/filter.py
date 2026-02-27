from fastapi import APIRouter, Query
from app.services.filter_service import filter_lessons

router = APIRouter()

@router.get("/")
async def get_filtered_lessons(
    class_id: str = Query(None, description="Mã lớp (VD: C10)"),
    subject_id: str = Query(None, description="Mã môn (VD: C10-TIN)"),
    topic_id: str = Query(None, description="Mã chủ đề (VD: C10-TIN-T01)"),
    lesson_id: str = Query(None, description="Mã bài học cụ thể"),
    start_date: str = Query(None, description="Từ ngày (YYYY-MM-DD)"),
    end_date: str = Query(None, description="Đến ngày (YYYY-MM-DD)"),
    limit: int = 20,
    offset: int = 0
):
    """
    Lọc dữ liệu bài học dựa trên cấu trúc phân cấp và thời gian từ PostgreSQL.
    """
    results = filter_lessons(
        class_id=class_id,
        subject_id=subject_id,
        topic_id=topic_id,
        lesson_id=lesson_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )
    
    return {
        "status": "success",
        "count": len(results),
        "data": results
    }