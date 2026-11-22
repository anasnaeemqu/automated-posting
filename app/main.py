from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_everywhere

app = FastAPI(title="Automated Multi-Platform Posting System")


@app.post("/posting", response_model=PostingResponse)
async def posting(req: PostingRequest):
    return await post_everywhere(req.message)