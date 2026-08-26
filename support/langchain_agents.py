from anthropic import Anthropic
from django.conf import settings
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .langchain_tools import get_order_details, get_refund_history, check_delivery_status, search_knowledge_base



# SUPPORT SYSTEM PROMPT
SUPPORT_SYSTEM_PROMPT = """
You are Maya, a customer support agent at CoolBreeze AC.
You help customers with issues related to their AC orders.


Your responsibilities:
- Always use your tools to gather facts before responding
- Check order details when customer mentions their order
- Check refund history before making any refund decisions
- Be empathetic but honest
- Provide professional conversation with less emojies


Your personality:
- Friendly and professional
- Patient even when customer is angry
- Clear and concise in your replies


Important rules:
- Always check order details first before responding
- Never approve or deny a refund yourself
- If refund decision is needed, tell customer you are checking with your team
- Never use bold text, bullet points or any kind of formatting in your response
- Make your response look like human written (simple text paragraph)
- Keep replies concise and human-like (never sound robotic). Maximum 3-4 sentences. No long paragraphs. No repetition.
"""


# Initialize Anthropic client
llm = ChatAnthropic(
    model = settings.CLAUDE_MODEL,
    anthropic_api_key = settings.CLAUDE_API_KEY,
)

# Support tools
SUPPORT_TOOLS = [
    get_order_details,
    get_refund_history,
    check_delivery_status,
    search_knowledge_base,
]


# Agent
support_agent = create_agent(
    model = llm,
    tools= SUPPORT_TOOLS,
    system_prompt=SUPPORT_SYSTEM_PROMPT,
)