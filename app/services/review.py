from openai import OpenAI
from langsmith import get_current_run_tree, traceable

from app.models import BLOCKED_PATTERNS, CodeReview, ReviewResponse, Severity


client = OpenAI()


def select_model(code: str) -> str:
    line_count = len(code.strip().splitlines())
    is_complex = any(
        keyword in code for keyword in ["class ", "async ", "lambda ", "decorator", "yield"]
    )

    if line_count > 50 or is_complex:
        return "gpt-4o"
    return "gpt-4o-mini"


@traceable(name="review_code")
def review_code_traced(code: str, language: str) -> ReviewResponse:
    run_guardrails(code, language)
    review = call_llm(code, language)
    validate_output(review)
    return ReviewResponse(language=language, review=review)


@traceable(name="llm_call")
def call_llm(code: str, language: str) -> CodeReview:
    model = select_model(code)
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a senior {language} code reviewer. "
                    "Be specific and practical. Score code on a scale of 1-10."
                ),
            },
            {"role": "user", "content": f"Review this code:\n\n{code}"},
        ],
        response_format=CodeReview,
    )

    usage = response.usage
    run = get_current_run_tree()
    if run and usage:
        run.end(
            metadata={
                "model": model,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "estimated_cost_usd": round(
                    (usage.prompt_tokens * 0.00000015)
                    + (usage.completion_tokens * 0.0000006),
                    6,
                ),
            }
        )

    return response.choices[0].message.parsed


@traceable(name="output_guardrails")
def validate_output(review: CodeReview) -> CodeReview:
    high_severity_issues = [issue for issue in review.issues if issue.severity == Severity.high]

    if high_severity_issues and review.score > 7:
        raise ValueError("Score too high for code with high severity issues")

    if review.score < 5 and not review.issues:
        raise ValueError("Low score must have at least one issue explaining why")

    if len(review.summary) < 20:
        raise ValueError("Summary too generic")

    return review


@traceable(name="guardrail_check")
def run_guardrails(code: str, language: str) -> bool:
    del language
    lowered = code.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in lowered:
            raise ValueError("Invalid input detected")
    return True
