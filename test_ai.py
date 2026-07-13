from pprint import pprint

from services.ai_client import run_prompt


result = run_prompt(
    prompt="Reply with exactly: Hello Dave",
)

pprint(result)