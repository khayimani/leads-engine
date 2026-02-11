from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import backend_core
import sqlite3

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/start-job")
async def start_job(role: str, industry: str, background_tasks: BackgroundTasks):
    # This runs the scraping in the background so the UI doesn't freeze
    background_tasks.add_task(backend_core.process_job, role, industry)
    return {"status": "started", "message": f"Scraping {role} in {industry}"}

@app.get("/leads")
async def get_leads():
    # Fetch data from the SQLite database
    conn = sqlite3.connect(backend_core.DB_NAME)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leads ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows