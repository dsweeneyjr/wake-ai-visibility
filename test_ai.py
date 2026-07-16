from pprint import pprint

from services.ai_client import run_prompt


result = run_prompt(
    prompt="What are the best community colleges near me?",
)

print(result)