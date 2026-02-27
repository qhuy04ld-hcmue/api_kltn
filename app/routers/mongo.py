from fastapi import APIRouter, Body
from app.database.mongo import db

router = APIRouter(prefix="/mongo")


@router.get("/collections")
def list_collections():
    return db.list_collection_names()


@router.get("/collection/{name}")
def get_collection(name: str):
    return list(db[name].find({}, {"_id": 0}).limit(200))


@router.post("/import/{name}")
def import_data(name: str, data: list = Body(...)):
    db[name].insert_many(data)
    return {"status": "imported"}
