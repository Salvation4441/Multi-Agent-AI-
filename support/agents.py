from anthropic import Anthropic
from django.conf import settings


# initializing
client = Anthropic(api_key=settings.CLAUDE_API_KEY)