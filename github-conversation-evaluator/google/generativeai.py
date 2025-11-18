"""Minimal local stub for google.generativeai used for development/testing.

This stub provides:
- configure(api_key=...)
- GenerationConfig: simple dataclass-like container
- GenerativeModel: simple class with generate_content(prompt) that returns a JSON string

This allows the rest of the project to run in a dry-run mode without the official
`google-generativeai` package. Replace or remove this shim when you install the
official client.
"""

import json
from dataclasses import dataclass
from typing import Any

_api_key = None

def configure(api_key: str | None = None):
    global _api_key
    _api_key = api_key

@dataclass
class GenerationConfig:
    temperature: float = 0.0
    response_mime_type: str = "application/json"

class GenerativeModel:
    def __init__(self, model_name: str, generation_config: GenerationConfig | None = None):
        self.model_name = model_name
        self.generation_config = generation_config or GenerationConfig()

    def generate_content(self, prompt: str) -> Any:
        # Return an object that has a .text attribute (like some clients do),
        # containing a valid JSON string that evaluation.py can parse.
        class Resp:
            def __init__(self, text: str):
                self.text = text
        # Produce a safe stubbed JSON that evaluation expects (Score, Justification)
        stub = {"Score": "STUB", "Justification": "This is a stub response from local generativeai shim."}
        return Resp(json.dumps(stub, ensure_ascii=False))
