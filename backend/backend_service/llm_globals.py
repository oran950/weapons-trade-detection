"""
LLM-specific global configuration
"""
import os

# LLM Provider Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# Triage thresholds
TRIAGE_LOW_THRESHOLD = float(os.getenv("TRIAGE_LOW_THRESHOLD", "0.35"))
TRIAGE_HIGH_THRESHOLD = float(os.getenv("TRIAGE_HIGH_THRESHOLD", "0.75"))

# Max LLM influence
MAX_LLM_SCORE_SHIFT = float(os.getenv("MAX_LLM_SCORE_SHIFT", "0.2"))

# Prompts
CLASSIFICATION_PROMPT = """You are validating *suspected illegal weapons trade* in academic research text.

Return STRICT JSON exactly with this schema (no prose, no backticks):
{
  "final_label": "HIGH"|"MEDIUM"|"LOW",
  "risk_adjustment": <number between -1.0 and 1.0>,
  "reasons": ["short bullet 1", "short bullet 2"],
  "evidence_spans": ["verbatim span 1", "verbatim span 2"],
  "misclassification_risk": "LOW"|"MEDIUM"|"HIGH"
}

Constraints:
- Do NOT invent evidence; spans must appear verbatim in the text.
- Consider benign contexts (airsoft, cosplay, museums, video games, news quotes) as LOW unless there is clear transaction intent.
- Strong indicators: weapon mention + transaction intent (buy/sell/price/contact), quantity, shipping/delivery, obfuscation.

INPUT
-----
TEXT:
\"\"\"{text}\"\"\"

RULE_FLAGS: {rule_flags}
KEYWORDS: {keywords}
PATTERNS: {patterns}
CURRENT_RULE_RISK: {rule_risk}
"""

ENTITY_EXTRACTION_PROMPT = """Extract entities from the following text related to weapons trade.

Return STRICT JSON with this schema (no prose, no backticks):
{
  "weapon_types": ["type1", "type2"],
  "weapon_models": ["model1", "model2"],
  "locations": ["location1", "location2"],
  "contact_methods": ["method1", "method2"],
  "prices": ["price1", "price2"],
  "quantities": ["qty1", "qty2"],
  "time_references": ["time1", "time2"]
}

Only include entities that actually appear in the text. Do not invent or infer.

TEXT:
\"\"\"{text}\"\"\"
"""

EXPLANATION_PROMPT = """Explain why the following flags were raised for this text.

Provide a clear, concise explanation for each flag. Focus on the specific evidence in the text.

TEXT:
\"\"\"{text}\"\"\"

FLAGS: {flags}

Explain each flag in 1-2 sentences.
"""

