from pydantic import BaseModel, Field

# ======================== REPORT MODELS ======================== #
# These models define the shape of request data for report-related endpoints.
# Pydantic validates incoming data automatically — if a required field is missing
# or has the wrong type, FastAPI returns a 422 error with details.

# ReportRequest — Used when a user starts a new report generation.
# The "..." in Field(...) means the field is required (must be provided).
# Example JSON: {"topic": "AI in Healthcare", "max_analysts": 3}
class ReportRequest(BaseModel):
    topic: str = Field(..., description="Topic for report generation")
    max_analysts: int = Field(3, description="Number of analyst personas to create")

# FeedbackRequest — Used when a user submits feedback on an in-progress report.
# thread_id identifies which report session to send feedback to.
# feedback defaults to an empty string if not provided.
# Example JSON: {"thread_id": "abc123", "feedback": "Add more statistics"}
class FeedbackRequest(BaseModel):
    thread_id: str
    feedback: str = ""

# ======================== AUTH MODELS ======================== #
# These models define the shape of request data for login and signup endpoints.
# They ensure username and password are always provided as strings.

# LoginRequest — Used when a user submits the login form.
# Both fields are required (Field(...) means mandatory).
# Example JSON: {"username": "john", "password": "secret123"}
class LoginRequest(BaseModel):
    username: str = Field(..., description="Username for login")
    password: str = Field(..., description="Password for login")

# SignupRequest — Used when a user submits the signup form to create a new account.
# Example JSON: {"username": "jane", "password": "mypassword"}
class SignupRequest(BaseModel):
    username: str = Field(..., description="New username for signup")
    password: str = Field(..., description="Password for signup")

# ReportFeedbackRequest — Used when a user submits a report topic along with optional feedback.
# Separated from ReportRequest to avoid class name conflict.
# "str | None" means the field accepts a string or null.
# Field(None) sets the default to None (not required).
# Example JSON: {"topic": "Climate Change"} or {"topic": "Climate Change", "feedback": "Focus on data"}
class ReportFeedbackRequest(BaseModel):
    topic: str = Field(..., description="Topic for report generation")
    feedback: str | None = Field(None, description="Optional feedback from analyst")