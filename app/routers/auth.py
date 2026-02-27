from fastapi import APIRouter, Form
from fastapi.responses import RedirectResponse
from app.database.postgres import get_conn

router = APIRouter()

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM acc WHERE username=%s AND password=%s",
        (username, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        response = RedirectResponse("/admin", status_code=302)
        response.set_cookie("admin", username)
        return response

    return RedirectResponse("/login", status_code=302)
