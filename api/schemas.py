from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    score: int  # 1 = thumbs up, 0 = thumbs down


class SourceItem(BaseModel):
    source: str
    page: int | None = None
    content: str


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str
