# Hướng Dẫn Khởi Động Hệ Thống

## 1. Khởi động MinIO

Mở Terminal (Command Prompt hoặc PowerShell) và chạy:

```bash
cd C:\minio
.\minio.exe server D:\minio-data --console-address ":9001"
```

---

## 2. Khởi động Neo4j

Mở Neo4j Desktop và chọn:

**Start Database: app**

---

## 3. Khởi động ứng dụng FastAPI

Mở Terminal tại thư mục project và chạy:

```bash
python -m uvicorn app.main:app --reload
```
