from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.api import file

from app.api import upload, import_data, crud, search, filter
from app.config import BUCKETS
from app.services.minio_service import client as minio_client

app = FastAPI(
    title="THPT Multimedia API",
    description="5 Luồng API - Postgres + MongoDB + Neo4j + MinIO",
    version="1.0.0"
)

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Register API Routers
# ==============================
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(import_data.router, prefix="/api/import", tags=["Import"])
app.include_router(crud.router, prefix="/api/crud", tags=["CRUD"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(filter.router, prefix="/api/filter", tags=["Filter"])
app.include_router(file.router, prefix="/api/file", tags=["File"])

# ==============================
# Startup Event
# ==============================
@app.on_event("startup")
def startup_event():
    print("🚀 Starting THPT Multimedia API...")

    for bucket in BUCKETS:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"✅ Created bucket: {bucket}")
        else:
            print(f"✔ Bucket exists: {bucket}")

    print("🎯 System Ready")


# ==============================
# Serve Frontend
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Serve file JS / CSS
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Trang chủ
@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Serve tất cả file .html
@app.get("/{page_name}.html", include_in_schema=False)
def serve_html(page_name: str):
    file_path = os.path.join(FRONTEND_DIR, f"{page_name}.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Page not found"}

@app.get("/login", include_in_schema=False)
def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/admin", include_in_schema=False)
def serve_admin():
    return FileResponse(os.path.join(FRONTEND_DIR, "admin.html"))

@app.get("/upload", include_in_schema=False)
def serve_upload():
    return FileResponse(os.path.join(FRONTEND_DIR, "upload.html"))

@app.get("/import", include_in_schema=False)
def serve_import():
    return FileResponse(os.path.join(FRONTEND_DIR, "import.html"))

@app.get("/crud", include_in_schema=False)
def serve_crud():
    return FileResponse(os.path.join(FRONTEND_DIR, "crud.html"))
