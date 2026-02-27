from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# IMPORT API BACKEND
from app.api import upload, import_data, crud, search, filter, file
from app.config import BUCKETS
from app.services.minio_service import client as minio_client

from fastapi import Form
from app.database.postgres import get_conn
app = FastAPI(
    title="THPT Multimedia System",
    version="2.0.0"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= REGISTER API =================


app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(import_data.router, prefix="/api/import", tags=["Import"])
app.include_router(crud.router, prefix="/api/crud", tags=["CRUD"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(filter.router, prefix="/api/filter", tags=["Filter"])
app.include_router(file.router, prefix="/api/file", tags=["File"])

# ================= STATIC + TEMPLATE =================
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ================= STARTUP =================
@app.on_event("startup")
def startup_event():
    print("🚀 Starting Multimedia Admin UI...")
    for bucket in BUCKETS:
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"✅ Created bucket: {bucket}")
        else:
            print(f"✔ Bucket exists: {bucket}")
    print("🎯 System Ready")


# ================= AUTH =================
def require_admin(request: Request):
    return request.cookies.get("admin")


# ================= PUBLIC =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(username: str = Form(...),
          password: str = Form(...)):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM acc WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return RedirectResponse("/login?error=1", status_code=302)

    response = RedirectResponse("/admin", status_code=302)
    response.set_cookie("admin", username)
    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("admin")
    return response


# ================= ADMIN =================
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@app.get("/admin/postgres", response_class=HTMLResponse)
def admin_postgres(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/postgres.html", {"request": request})


@app.get("/admin/mongo", response_class=HTMLResponse)
def admin_mongo(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/mongo.html", {"request": request})


@app.get("/admin/minio", response_class=HTMLResponse)
def admin_minio(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/minio.html", {"request": request})

@app.get("/admin/search", response_class=HTMLResponse)
def admin_search(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/search.html", {"request": request})


@app.get("/admin/filter", response_class=HTMLResponse)
def admin_filter(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/filter.html", {"request": request})


@app.get("/admin/crud", response_class=HTMLResponse)
def admin_crud(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/crud.html", {"request": request})


@app.get("/admin/upload", response_class=HTMLResponse)
def admin_upload(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/upload.html", {"request": request})


@app.get("/admin/import", response_class=HTMLResponse)
def admin_import(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/import.html", {"request": request})

@app.get("/admin/neo4j", response_class=HTMLResponse)
def admin_neo4j(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/neo4j.html", {"request": request})

from app.api import postgres

app.include_router(postgres.router)

'''
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from app.routers import auth, postgres, mongo, neo4j, minio, search, filter
from app.routers import public



app = FastAPI()
app.include_router(public.router)
# ================= ROUTERS =================
app.include_router(auth.router)
app.include_router(postgres.router)
app.include_router(mongo.router)
app.include_router(neo4j.router)
app.include_router(minio.router)
app.include_router(search.router)
app.include_router(filter.router)

# ================= STATIC =================
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ================= AUTH CHECK =================
def require_admin(request: Request):
    return request.cookies.get("admin")


# ================= PUBLIC =================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("admin")
    return response


# ================= ADMIN =================
@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request}
    )


@app.get("/admin/postgres", response_class=HTMLResponse)
def admin_postgres(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/postgres.html", {"request": request})


@app.get("/admin/mongo", response_class=HTMLResponse)
def admin_mongo(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/mongo.html", {"request": request})


@app.get("/admin/neo4j", response_class=HTMLResponse)
def admin_neo4j(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/neo4j.html", {"request": request})


@app.get("/admin/minio", response_class=HTMLResponse)
def admin_minio(request: Request):
    if not require_admin(request):
        return RedirectResponse("/login")
    return templates.TemplateResponse("admin/minio.html", {"request": request})

'''





'''
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
'''