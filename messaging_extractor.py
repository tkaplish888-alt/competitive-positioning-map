import json
import anthropic
from config import ANTHROPIC_API_KEY, EMBEDDING_MODEL  # noqa: F401 – EMBEDDING_MODEL imported for callers

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_MODEL = "claude-opus-4-6"

_SYSTEM_PROMPT = (
    "You are a marketing strategist specializing in competitive positioning analysis. "
    "When given website copy, focus exclusively on how the company positions itself in the market — "
    "its messaging, audience, and differentiation strategy — not on product features or technical details. "
    "Return only valid JSON with no additional commentary."
)

_USER_TEMPLATE = """\
Analyze the marketing positioning of {company} based on the following website copy and return a JSON object with these exact fields:

- value_propositions: list of 2-4 core value propositions as short phrases
- target_audience: a concise description of who the product is aimed at
- key_claims: list of 3-5 specific claims the company makes about itself
- differentiators: what sets this company apart from alternatives
- tone: 1-2 words describing the brand voice (e.g. "professional, reassuring")
- positioning_summary: exactly 2 sentences summarising the company's market position

Website copy:
{text}
"""

_MAX_INPUT_CHARS = 8000


def extract_messaging(company: str, raw_text: str) -> dict:
    """Call Claude to extract structured positioning data from raw website copy.

    Args:
        company: Display name of the company (used in the prompt).
        raw_text: Raw scraped website text. Truncated to 8 000 characters.

    Returns:
        Parsed dict with keys: value_propositions, target_audience, key_claims,
        differentiators, tone, positioning_summary.
    """
    truncated = raw_text[:_MAX_INPUT_CHARS]

    message = _client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": _USER_TEMPLATE.format(company=company, text=truncated),
            }
        ],
    )

    raw_response = message.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the JSON
    if raw_response.startswith("```"):
        lines = raw_response.splitlines()
        # Drop the opening fence (```json or ```) and the closing fence (```)
        lines = lines[1:] if lines[0].startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        raw_response = "\n".join(lines).strip()

    return json.loads(raw_response)


def create_embedding_text(messaging: dict) -> str:
    """Flatten a structured messaging dict into a single string for embedding.

    Fields are ordered and pipe-separated so adjacent sections stay distinct:
    value_propositions → target_audience → key_claims → differentiators → positioning_summary.

    Args:
        messaging: Dict as returned by extract_messaging.

    Returns:
        A single string suitable for passing to the embedding model.
    """
    value_props = " ".join(messaging.get("value_propositions", []))
    audience = messaging.get("target_audience", "")
    claims = " ".join(messaging.get("key_claims", []))
    differentiators = messaging.get("differentiators", "")
    summary = messaging.get("positioning_summary", "")

    return " | ".join([value_props, audience, claims, differentiators, summary])
