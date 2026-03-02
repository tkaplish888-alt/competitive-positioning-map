import anthropic
from config import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

_MODEL = "claude-opus-4-6"

_SYSTEM_PROMPT = (
    "You are a competitive intelligence analyst writing for a VP of Marketing. "
    "Your job is to interpret positioning data and deliver sharp, specific insight "
    "that can directly inform messaging strategy. "
    "Write in flowing paragraphs, not bullet points. "
    "Always ground your observations in exact language from the extracted messaging — "
    "quote or paraphrase specific phrases rather than giving generic category-level commentary. "
    "Be direct about threats and opportunities. The reader wants actionable intelligence, not hedged summaries."
)

_CONTEXT_TEMPLATE = """\
Company being analysed: {your_company}

Below is the extracted positioning data for each player in this market, \
along with their cosine similarity score to {your_company} \
(1.0 = identical positioning, 0.0 = completely different).

{competitor_blocks}
"""

_COMPETITOR_BLOCK_TEMPLATE = """\
── {name} (similarity to {your_company}: {similarity}) ──
Positioning summary : {positioning_summary}
Value propositions  : {value_propositions}
Target audience     : {target_audience}
Differentiators     : {differentiators}
Tone                : {tone}
"""

_USER_PROMPT = """\
Write a competitive intelligence brief of 300-400 words covering exactly these four sections \
(use the section names as plain prose headers, not as bullet points):

1. Positioning clusters — who is saying similar things, and what shared themes or language unite them?
2. Threat assessment — which competitor is closest to {your_company}'s positioning, why does that matter, \
and what specific overlapping claims create the most risk?
3. White space — where in this market is nobody currently positioned, and what genuine opportunity does that create?
4. Recommendations — 1-2 specific, concrete actions {your_company} should take based on the above, \
referencing actual language gaps or overcrowded territory you identified.

Positioning data:

{context}
"""


def generate_analysis(
    your_company: str,
    messaging_data: dict[str, dict],
    similarities: dict[str, float],
) -> str:
    """Use Claude to write a competitive intelligence brief from structured positioning data.

    Args:
        your_company:   Display name of the company being analysed (e.g. "Valur").
        messaging_data: Dict of company_key → messaging dict from extract_messaging.
        similarities:   Dict of company_key → cosine similarity float vs. your company.

    Returns:
        The brief as a plain text string (paragraphs, no markdown bullets).
    """
    competitor_blocks = []
    for key, messaging in messaging_data.items():
        similarity = similarities.get(key, 0.0)
        value_props = messaging.get("value_propositions", [])
        block = _COMPETITOR_BLOCK_TEMPLATE.format(
            name=messaging.get("company_name", key),
            your_company=your_company,
            similarity=f"{similarity:.3f}",
            positioning_summary=messaging.get("positioning_summary", "—"),
            value_propositions="; ".join(value_props) if value_props else "—",
            target_audience=messaging.get("target_audience", "—"),
            differentiators=messaging.get("differentiators", "—"),
            tone=messaging.get("tone", "—"),
        )
        competitor_blocks.append(block)

    context = _CONTEXT_TEMPLATE.format(
        your_company=your_company,
        competitor_blocks="\n".join(competitor_blocks),
    )

    user_prompt = _USER_PROMPT.format(
        your_company=your_company,
        context=context,
    )

    message = _client.messages.create(
        model=_MODEL,
        max_tokens=1024,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text.strip()
