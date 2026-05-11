import json
from pathlib import Path
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (Path(__file__).parent.parent / "resources" / "system_prompt.md").read_text()

DECISION_TOOL = {
    "name": "make_inverter_decision",
    "description": "Decide whether to switch inverter to Selling First mode today and at what times.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sell_today": {
                "type": "boolean",
                "description": "Whether conditions justify switching to Selling First mode today"
            },
            "sell_from": {
                "type": ["string", "null"],
                "description": "HH:MM local time to start selling, or null if not selling today"
            },
            "sell_until": {
                "type": ["string", "null"],
                "description": "HH:MM local time to stop selling, or null if not selling today"
            },
            "reasoning": {
                "type": "string",
                "description": "Brief explanation of the decision based on the forecast data"
            }
        },
        "required": ["sell_today", "sell_from", "sell_until", "reasoning"]
    }
}


def decide(forecast: dict) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        tools=[DECISION_TOOL],
        tool_choice={"type": "tool", "name": "make_inverter_decision"},
        messages=[{
            "role": "user",
            "content": f"Today's forecast:\n{json.dumps(forecast, indent=2)}"
        }]
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "make_inverter_decision":
            return block.input
    raise RuntimeError("Claude did not return a decision tool use block")
