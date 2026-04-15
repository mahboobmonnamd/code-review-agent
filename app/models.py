from enum import Enum

from pydantic import BaseModel, Field, field_validator


BLOCKED_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "jailbreak",
]

SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "sql", "java", "go"}


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Issue(BaseModel):
    line: str
    severity: Severity
    description: str


class CodeReview(BaseModel):
    summary: str
    issues: list[Issue]
    suggestions: list[str]
    score: int = Field(ge=1, le=10)


class ReviewRequest(BaseModel):
    code: str = Field(min_length=10, max_length=5000)
    language: str = Field(default="python", min_length=2, max_length=20)

    @field_validator("code")
    @classmethod
    def no_prompt_injection(cls, value: str) -> str:
        lowered = value.lower()
        for pattern in BLOCKED_PATTERNS:
            if pattern in lowered:
                raise ValueError("Invalid input detected")
        return value

    @field_validator("language")
    @classmethod
    def supported_language(cls, value: str) -> str:
        normalized = value.lower()
        if normalized not in SUPPORTED_LANGUAGES:
            supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
            raise ValueError(f"Unsupported language. Choose from: {supported}")
        return normalized


class ReviewResponse(BaseModel):
    language: str
    review: CodeReview
