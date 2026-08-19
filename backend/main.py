from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from backend.generate import generate_pattern
from backend.db import store_pattern, get_pattern_by_id
from backend.export import pattern_to_pdf

app = FastAPI(title="Crochet Pattern Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    description: str

@app.post("/generate")
def generate(req: GenerateRequest):
    pattern, inspiration = generate_pattern(req.description)
    pid = store_pattern(pattern)
    return {"id": pid, "pattern": pattern.model_dump(), "inspiration": inspiration}

@app.get("/pattern/{pattern_id}")
def get_pattern(pattern_id: str):
    p = get_pattern_by_id(pattern_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return p.model_dump()

@app.get("/export/{pattern_id}")
def export_pdf(pattern_id: str, uk: bool = False):
    p = get_pattern_by_id(pattern_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pattern not found")
    pdf = pattern_to_pdf(p, uk_terms=uk)
    return Response(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{p.title}.pdf"'},
    )
