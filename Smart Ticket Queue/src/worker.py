import os
from pathlib import Path
from celery import Celery
from dotenv import load_dotenv
from openai import OpenAI
from src.llm.schema import TicketAnalysisOutput

# Load environment variables
load_dotenv()

# Initialize Celery app
celery_app = Celery(
    "ticket_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Determine the absolute path to the prompt file
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = BASE_DIR / "prompts" / "triage-v1.md"

@celery_app.task(bind=True, max_retries=3, retry_backoff=True)
def process_ticket_task(self, ticket_text: str):
    """
    Process a customer support ticket using an LLM to extract triage information.
    Includes automatic retries for API failures or timeouts.
    """
    try:
        # If LLM_STUB=1 is set, bypass the API and return a mock response immediately.
        if os.getenv("LLM_STUB") == "1":
            print("LLM_STUB is enabled. Returning mock response.")
            mock_data = {
                "category": "BILLING",
                "urgency": "HIGH",
                "summary": "The customer was charged twice for their subscription.",
                "action_required": True
            }
            # Validate and return the mock data
            return TicketAnalysisOutput.model_validate(mock_data).model_dump()

        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is not set.")

        # Read the system prompt
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        # Initialize OpenAI client (safe for multi-processing)
        client_kwargs = {"api_key": api_key}
        
        # Support optional base_url for OpenRouter or other OpenAI-compatible APIs
        base_url = os.getenv("LLM_BASE_URL")
        if base_url:
            client_kwargs["base_url"] = base_url
            
        client = OpenAI(**client_kwargs)
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")

        # Call the LLM API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": ticket_text}
            ],
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Received empty content from LLM API.")

        # Validate output using the Pydantic schema
        validated_output = TicketAnalysisOutput.model_validate_json(content)

        # Return validated data as a dictionary (JSON serializable for Celery backend)
        return validated_output.model_dump()

    except Exception as exc:
        # Automatic retries for any exception (e.g., timeouts, rate limits, validation errors)
        print(f"Task failed with error: {exc}. Retrying...")
        raise self.retry(exc=exc)
