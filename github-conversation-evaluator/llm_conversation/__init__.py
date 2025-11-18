"""Package exports for llm_conversation.

This module re-exports commonly used symbols from submodules and, when
available, exposes selected helpers from google.generativeai (configure,
GenerationConfig, GenerativeModel) so callers can import them from
`llm_conversation`.
"""

from pathlib import Path

# Submodules may depend on optional third-party packages. Import them
# lazily / defensively so `import llm_conversation` works even when some
# optional deps are missing (e.g. when running only evaluation scripts
# that rely on `google.generativeai`).
try:
	from .ai_agent import AIAgent
except Exception:  # pragma: no cover - optional dependency missing
	AIAgent = None

try:
	from .color import generate_distinct_colors, rgb_to_ansi16, rgb_to_ansi256
except Exception:  # pragma: no cover - optional dependency missing
	generate_distinct_colors = None
	rgb_to_ansi16 = None
	rgb_to_ansi256 = None

try:
	from .config import AgentConfig, get_available_models, load_config
except Exception:  # pragma: no cover - optional dependency missing
	AgentConfig = None
	get_available_models = None
	load_config = None

try:
	from .conversation_manager import ConversationManager, TurnOrder
except Exception:  # pragma: no cover - optional dependency missing
	ConversationManager = None
	TurnOrder = None

try:
	from .logging_config import get_logger, setup_logging
except Exception:  # pragma: no cover - optional dependency missing
	get_logger = None
	setup_logging = None

# Optional: expose google.generativeai helpers if the package is installed.
try:
	import google.generativeai as genai  # type: ignore
except Exception:
	genai = None

configure = getattr(genai, "configure", None)
GenerationConfig = getattr(genai, "GenerationConfig", None)
GenerativeModel = getattr(genai, "GenerativeModel", None)

__all__ = [
	"AIAgent",
	"generate_distinct_colors",
	"rgb_to_ansi16",
	"rgb_to_ansi256",
	"AgentConfig",
	"get_available_models",
	"load_config",
	"ConversationManager",
	"TurnOrder",
	"get_logger",
	"setup_logging",
	"configure",
	"GenerationConfig",
	"GenerativeModel",
]

