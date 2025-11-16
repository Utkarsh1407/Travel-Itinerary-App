from fastapi import FastAPI
from pydantic import BaseModel
from .rag_engine import TravelRAG

app = FastAPI()
rag = TravelRAG()

class Query(BaseModel):
    country: str
    city: str
    duration: int
    budget: int
    question: str | None = None

@app.post("/top-places")
async def fetch_places(data: Query):
    return {"places": rag.get_top_places(data.city, data.country)}

@app.post("/itinerary")
async def generate_itinerary(data: Query):
    itinerary = rag.create_itinerary(
        data.city, data.country, data.duration, data.budget
    )
    return {"itinerary": itinerary}

@app.post("/ask")
async def answer_query(data: Query):
    return {"answer": rag.answer_question(data.question)}
