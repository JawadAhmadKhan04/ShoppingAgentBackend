# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import ShoppingAgent, GeminiLLM  # your existing agent code
from typing import Any
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()

app = FastAPI(title="Shopping Agent Backend")

# Health check endpoint for Render
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Initialize your LLM and agent
llm = GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))
agent = ShoppingAgent(llm=llm)

# Request model
class Query(BaseModel):
    output: str

# API endpoint
@app.post("/search")
def search_product(query: Query):
    print(query)
    print("----------------------------------------------------------------")
    # print(query.output)
    result = agent.run(query.output)
    
    return {"result": result}
