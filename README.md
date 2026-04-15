# Code Review Agent

A small FastAPI application that reviews source code using the OpenAI API and returns a structured response with:

- a summary
- identified issues with severity
- improvement suggestions
- an overall score from 1 to 10

## Requirements

- Python 3.12+
- `uv`
- an `OPENAI_API_KEY` environment variable

## Installation

```bash
uv sync
```

If you use a `.env` file locally, make sure it contains your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

## Project Structure

The app is now split into a few focused modules:

- `main.py` loads environment variables and exposes the FastAPI app for `uvicorn`.
- `app/api.py` defines the FastAPI app and the `/review` route.
- `app/models.py` contains request and response schemas plus validation rules.
- `app/services/review.py` contains the review workflow, LLM call, and guardrails.

## Run the App

Use:

```bash
uvicorn main:app --reload
```

The app will start locally at:

```text
http://127.0.0.1:8000
```

FastAPI docs will be available at:

```text
http://127.0.0.1:8000/docs
```

## API Overview

### `POST /review`

This endpoint accepts a code snippet and a language, sends the request to OpenAI, and returns a structured review.

### Request body

```json
{
  "code": "def add(a, b):\n    return a+b",
  "language": "python"
}
```

### Supported languages

- `python`
- `javascript`
- `typescript`
- `sql`
- `java`
- `go`

### Example response

```json
{
  "language": "python",
  "review": {
    "summary": "Simple function with acceptable readability, but formatting can be improved.",
    "issues": [
      {
        "line": "2",
        "severity": "low",
        "description": "Spacing around the operator does not follow common style conventions."
      }
    ],
    "suggestions": [
      "Use standard formatting such as `a + b` for readability."
    ],
    "score": 7
  }
}
```

## Quick Test

Once the server is running, you can test it with:

```bash
curl -X POST "http://127.0.0.1:8000/review" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def add(a, b):\n    return a+b",
    "language": "python"
  }'
```

## Notes

- The OpenAI client expects `OPENAI_API_KEY` to be available in the environment.
- The project currently exposes one API endpoint: `POST /review`.
- The app chooses between `gpt-4o-mini` and `gpt-4o` based on code size and complexity.
