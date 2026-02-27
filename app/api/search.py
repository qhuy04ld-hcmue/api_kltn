from fastapi import APIRouter, Query
from app.services.search_service import search_by_keyword, search_by_graph

router = APIRouter()

@router.get("/keyword")
async def search_lessons_by_keyword(
    q: str = Query(..., min_length=2, description="Từ khóa tìm kiếm"),
    limit: int = 20,
    offset: int = 0
):
    """
    Tìm kiếm bài học theo từ khóa trong tiêu đề, nội dung phân đoạn hoặc từ khóa liên quan.
    """
    results = search_by_keyword(keyword=q, limit=limit, offset=offset)
    return {
        "status": "success",
        "data": results
    }

@router.get("/graph")
async def search_lessons_by_graph(
    class_id: str = None,
    subject_id: str = None,
    topic_id: str = None
):
    """
    Tìm kiếm dựa trên mối quan hệ đồ thị (Graph) trong Neo4j.
    """
    results = search_by_graph(
        class_id=class_id, 
        subject_id=subject_id, 
        topic_id=topic_id
    )
    return {
        "status": "success",
        "data": results
    }