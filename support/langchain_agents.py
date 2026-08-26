from anthropic import Anthropic
from django.conf import settings
from langchain_anthropic import ChatAnthropic

# Initialize Anthropic client
llm = ChatAnthropic(
    model = settings.CLAUDE_MODEL,
    anthropic_api_key = settings.CLAUDE_API_KEY,
)
