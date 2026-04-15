from fastapi import FastAPI, HTTPException

from app.models import ReviewRequest, ReviewResponse
from app.services.review import review_code_traced


app = FastAPI()


@app.post("/review", response_model=ReviewResponse)
def review_code(request: ReviewRequest) -> ReviewResponse:
    try:
        return review_code_traced(request.code, request.language)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
