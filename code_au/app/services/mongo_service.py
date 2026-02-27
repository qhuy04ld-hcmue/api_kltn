from pymongo import MongoClient
from datetime import datetime
from app.config import MONGO_URL, MONGO_DB

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

classes_col = db["classes"]
subjects_col = db["subjects"]
topics_col = db["topics"]
lessons_col = db["lessons"]

# ==============================
# STRUCTURE SYNC
# ==============================

def sync_class(class_code, class_name):
    classes_col.update_one(
        {"class_id": class_code},
        {"$set": {
            "class_id": class_code,
            "class_name": class_name,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_subject(subject_id, class_code, subject_code):
    subjects_col.update_one(
        {"subject_id": subject_id},
        {"$set": {
            "subject_id": subject_id,
            "class_id": class_code,
            "subject_code": subject_code,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_topic(topic_id, subject_id, topic_order):
    topics_col.update_one(
        {"topic_id": topic_id},
        {"$set": {
            "topic_id": topic_id,
            "subject_id": subject_id,
            "topic_order": topic_order,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_lesson_structure(lesson_id, topic_id, lesson_order, lesson_name=None):
    lessons_col.update_one(
        {"lesson_id": lesson_id},
        {"$setOnInsert": {
            "lesson_id": lesson_id,
            "topic_id": topic_id,
            "lesson_order": lesson_order,
            "lesson_name": lesson_name,
            "files": [],
            "is_deleted": False,
            "created_at": datetime.utcnow()
        }},
        upsert=True
    )

# ==============================
# FILE METADATA
# ==============================

def add_file_to_lesson(lesson_id, metadata):
    lessons_col.update_one(
        {"lesson_id": lesson_id},
        {
            "$push": {
                "files": {
                    "file_name": metadata["file_name"],
                    "file_url": metadata["file_url"],
                    "bucket": metadata["bucket"],
                    "uploaded_at": datetime.utcnow()
                }
            }
        }
    )

# ==============================
# CRUD SUPPORT
# ==============================

def update_lesson_metadata(lesson_id, lesson_name=None):
    update_fields = {}

    if lesson_name:
        update_fields["lesson_name"] = lesson_name

    if update_fields:
        lessons_col.update_one(
            {"lesson_id": lesson_id},
            {"$set": update_fields}
        )


def soft_delete_lesson(lesson_id):
    lessons_col.update_one(
        {"lesson_id": lesson_id},
        {"$set": {"is_deleted": True}}
    )

# ==============================
# SEARCH / FILTER SUPPORT
# ==============================

def get_lesson_files(lesson_id: str):
    lesson = lessons_col.find_one(
        {"lesson_id": lesson_id, "is_deleted": {"$ne": True}}
    )

    if not lesson:
        return []

    return lesson.get("files", [])



'''
from pymongo import MongoClient
from datetime import datetime
from app.config import MONGO_URL, MONGO_DB

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]

# Collections
classes_col = db["classes"]
subjects_col = db["subjects"]
topics_col = db["topics"]
lessons_col = db["lessons"]


# ==============================
# STRUCTURE SYNC
# ==============================

def sync_class(class_code, class_name):
    classes_col.update_one(
        {"class_id": class_code},
        {"$set": {
            "class_id": class_code,
            "class_name": class_name,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_subject(subject_id, class_code, subject_code):
    subjects_col.update_one(
        {"subject_id": subject_id},
        {"$set": {
            "subject_id": subject_id,
            "class_id": class_code,
            "subject_code": subject_code,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_topic(topic_id, subject_id, topic_order):
    topics_col.update_one(
        {"topic_id": topic_id},
        {"$set": {
            "topic_id": topic_id,
            "subject_id": subject_id,
            "topic_order": topic_order,
            "updated_at": datetime.utcnow()
        }},
        upsert=True
    )


def sync_lesson_structure(lesson_id, topic_id, lesson_order):
    lessons_col.update_one(
        {"lesson_id": lesson_id},
        {"$setOnInsert": {
            "lesson_id": lesson_id,
            "topic_id": topic_id,
            "lesson_order": lesson_order,
            "files": []
        }},
        upsert=True
    )


# ==============================
# FILE METADATA
# ==============================

def add_file_to_lesson(lesson_id, metadata):
    # 1️⃣ Push vào lesson.files[]
    lessons_col.update_one(
        {"lesson_id": lesson_id},
        {
            "$push": {
                "files": {
                    "file_name": metadata["file_name"],
                    "file_url": metadata["file_url"],
                    "bucket": metadata["bucket"],
                    "uploaded_at": datetime.utcnow()
                }
            }
        }
    )

    # 2️⃣ Insert vào collection riêng theo bucket
    db[metadata["bucket"]].insert_one({
        "lesson_id": lesson_id,
        "file_name": metadata["file_name"],
        "file_url": metadata["file_url"],
        "class": metadata["class"],
        "subject": metadata["subject"],
        "topic": metadata["topic"],
        "lesson": metadata["lesson"],
        "uploaded_at": datetime.utcnow()
    })
#support for crud
def update_lesson_metadata(lesson_id, lesson_name=None):
    update_fields = {}

    if lesson_name:
        update_fields["lesson_name"] = lesson_name

    if update_fields:
        db["lessons"].update_one(
            {"lesson_id": lesson_id},
            {"$set": update_fields}
        )


def soft_delete_lesson(lesson_id):
    db["lessons"].update_one(
        {"lesson_id": lesson_id},
        {"$set": {"is_deleted": True}}
    )

# support for search and filter
def get_lesson_files(lesson_id: str):
    lesson = db.lessons.find_one({"lesson_id": lesson_id})

    if not lesson:
        return []

    return lesson.get("files", [])
'''