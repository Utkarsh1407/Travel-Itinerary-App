import os
import requests
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

class TravelRAG:

    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-8b-instant"
        )
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.retriever = None
        self.places = []

    def get_top_places(self, city, country, limit=10):
        api_key = os.getenv("GEOAPIFY_API_KEY")

        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": f"{city}, {country}", "format": "json", "limit": 1},
            headers={"User-Agent": "Mozilla/5.0"}
        ).json()

        if not geo:
            return []

        lat, lon = geo[0]["lat"], geo[0]["lon"]

        url = "https://api.geoapify.com/v2/places"
        params = {
            "categories": "tourism",
            "filter": f"circle:{lon},{lat},10000",
            "limit": limit,
            "apiKey": api_key
        }
        data = requests.get(url, params=params).json()
        feats = data.get("features", [])

        self.places = [f"{p['properties'].get('name','Unknown')} - {p['properties'].get('formatted','')}" for p in feats]

        docs = [Document(page_content=place) for place in self.places]
        vect = FAISS.from_documents(docs, self.embeddings)
        self.retriever = vect.as_retriever()

        return self.places

    def create_itinerary(self, city, country, duration, budget):
        prompt = f"""
        Create a {duration}-day travel itinerary for {city}, {country}.
        Total budget: ₹{budget}
        Use these places:
        {chr(10).join(self.places)}
        """

        response = self.llm.invoke(prompt)
        return response.content

    def answer_question(self, user_q):
        docs = self.retriever.get_relevant_documents(user_q)
        context = "\n".join(d.page_content for d in docs)

        prompt = f"""
        Use the following places as context:
        {context}
        Question: {user_q}
        """

        response = self.llm.invoke(prompt)
        return response.content
