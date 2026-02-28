from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from src.database.database_config import SessionLocal, User, hash_password, verify_password
from src.api.services.report_service import ReportService

# APIRouter groups related endpoints together so they can be registered with the FastAPI app.
# Example: router.get("/login") will be accessible at http://localhost:8000/login
router = APIRouter()

# In-memory session store. Maps session IDs to usernames.
# Example: {"john_session": "john", "jane_session": "jane"}
SESSIONS = {}

# Database dependency generator. Creates a new database session for each request
# and ensures it is closed after use, even if an error occurs.
# Example usage: db = next(get_db())
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================== AUTH ROUTES ======================== #
# Handles user login, signup, and session management.
# Login flow:  GET / (show form) -> POST /login (authenticate)
# Signup flow: GET /signup (show form) -> POST /signup (create user)

# GET / — Renders the login page.
# Example: User visits http://localhost:8000/ and sees the login form.
@router.get("/", response_class=HTMLResponse)
async def show_login(request: Request):
    return request.app.templates.TemplateResponse("login.html", {"request": request})

# POST /login — Authenticates the user with username and password from the login form.
# On success: creates a session cookie and redirects to /dashboard.
# On failure: re-renders login page with an error message.
# Example: User submits username="john" and password="secret123"
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if user and verify_password(password, user.password):
        # Create a simple session ID and store it in the in-memory SESSIONS dict.
        # Example: session_id = "john_session"
        session_id = f"{username}_session"
        SESSIONS[session_id] = username
        response = RedirectResponse(url="/dashboard", status_code=302)
        # Set a cookie so the browser sends the session_id on subsequent requests.
        response.set_cookie(key="session_id", value=session_id)
        return response

    return request.app.templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid username or password"},
    )

# GET /signup — Renders the signup page.
# Example: User visits http://localhost:8000/signup and sees the registration form.
@router.get("/signup", response_class=HTMLResponse)
async def show_signup(request: Request):
    return request.app.templates.TemplateResponse("signup.html", {"request": request})

# POST /signup — Creates a new user account.
# Checks if the username already exists. If not, hashes the password and saves to the database.
# On success: redirects to the login page.
# On failure: re-renders signup page with an error message.
# Example: User submits username="jane" and password="mypassword"
@router.post("/signup", response_class=HTMLResponse)
async def signup(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return request.app.templates.TemplateResponse(
            "signup.html", {"request": request, "error": "Username already exists"}
        )

    hashed_pw = hash_password(password)
    new_user = User(username=username, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/", status_code=302)

# ======================== REPORT ROUTES ======================== #
# Handles the report generation workflow:
# 1. User lands on dashboard -> enters a topic -> generates a report
# 2. User can submit feedback to refine the report
# 3. User can download the final report as DOCX/PDF

# GET /dashboard — Renders the main dashboard page for authenticated users.
# Checks the session cookie to verify the user is logged in.
# If not logged in, redirects back to the login page.
# Example: Authenticated user sees the dashboard with a form to enter a report topic.
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id not in SESSIONS:
        return RedirectResponse(url="/")
    return request.app.templates.TemplateResponse("dashboard.html", {"request": request, "user": SESSIONS[session_id]})

# POST /generate_report — Starts the report generation workflow for a given topic.
# Creates a ReportService instance and kicks off generation with a max of 3 iterations.
# Returns a progress page where the user can track and provide feedback.
# Example: User submits topic="AI in Healthcare" -> report generation begins.
@router.post("/generate_report", response_class=HTMLResponse)
async def generate_report(request: Request, topic: str = Form(...), max_analysts: int = Form(1)):
    service = ReportService()
    result = service.start_report_generation(topic, max_analysts)
    # thread_id uniquely identifies this report generation session for feedback/status tracking.
    thread_id = result["thread_id"]

    return request.app.templates.TemplateResponse(
        "report_progress.html",
        {
            "request": request,
            "topic": topic,
            "feedback": "",
            "thread_id": thread_id,
        },
    )

# POST /submit_feedback — Submits user feedback to refine an in-progress report.
# After submitting, fetches the latest report status to check if DOCX/PDF files are ready.
# Example: User submits feedback="Add more statistics" for thread_id="abc123"
@router.post("/submit_feedback", response_class=HTMLResponse)
async def submit_feedback(request: Request, topic: str = Form(...), feedback: str = Form(...), thread_id: str = Form(...)):
    service = ReportService()
    service.submit_feedback(thread_id, feedback)

    # Fetch the current report status to check if downloadable files are available.
    result = service.get_report_status(thread_id)
    doc_path = result.get("docx_path")
    pdf_path = result.get("pdf_path")

    return request.app.templates.TemplateResponse(
        "report_progress.html",
        {
            "request": request,
            "topic": topic,
            "feedback": feedback,
            "doc_path": doc_path,
            "pdf_path": pdf_path,
            "thread_id": thread_id,
        },
    )

# GET /download/{file_name} — Downloads a generated report file (DOCX or PDF).
# Looks up the file by name and returns it as a downloadable response.
# Returns an error dict if the file is not found.
# Example: GET /download/report_ai_in_healthcare.pdf -> downloads the PDF file.
@router.get("/download/{file_name}")
async def download_report(file_name: str):
    service = ReportService()
    file_response = service.download_file(file_name)
    if file_response:
        return file_response
    return {"error": f"File {file_name} not found"}