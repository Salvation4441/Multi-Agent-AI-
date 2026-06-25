from anthropic import Anthropic
from django.conf import settings
from .tools import *
from . models import *


# initializing anthropic client
client = Anthropic(api_key=settings.CLAUDE_API_KEY)
model = settings.CLAUDE_MODEL


# CREATING 4 COMPONENT

# 1. SUPPORT SYSTEM PROMPT
SUUPORT_SYSYTEM_PROMPT = """
You are Maya, a customer support agent at CoolBreeze AC.
You help customers with issues related to their AC orders.


Your responsibilities:
- Always use your tools to gather facts before responding
- Check order details when customer mentions their order
- Check refund history before making any refund decisions
- Be empahetic but honest
- Provide professional conversation with less emojies


Your personality:
- Friendly and professional
- Patient even when customer is angry
- Clear and concise in your replies


Important rules:
- Always check order details first before responding
- Never approve or deny a refund yourself
- If refund decision is needed, tell customer you are checking with your team
"""



# 2. SUPPORT TOOLS --> Tools schemas ,that the AI agent reads
SUPPORT_TOOLS = [
    # getting order details
    {
        "name" : "get_order_details",
        "description" : "Fetch complete order details including status, carrier, tracking number and days since order was placed. Use this when customer mentions their order or complains about delivery",
        "input_schema": {
            "type" : "object",
            "properties": {
                "order_id":{
                   "type" : "integer",
                   "description" : "THe order ID to look up"
                }
            },
            "required":["order_id"]
        }
    },

    # get refund history
    {
        "name" : "get_refund_history",
        "description" : "Get complete refund history for a user. Use this before making any refund related decisions.",
        "input_schema":{
            "type":"object",
            "properties":{
                "user_id":{
                    "type":"integer",
                    "description":"The user ID to check refund history for"
                }
            },
            "required":["user_id"]
        }
    },
    

    # checking for the delivery status
    {
        "name" : "check_delivery_status",
        "description" : "Check current delivery status using tracking number and carrier. Use this when customer complains about delayed or missing delivery.",
        "input_schema":{
            "type":"object",
            "properties":{
                "tracking_number":{
                    "type":"string",
                    "description":"The shipment tracking number"
                },
                "carrier":{
                    "type":"string",
                    "description":"The carrier name for exmaple BLueDart or Delhivery"
                }
            },
            "required":["tracking_number","carrier"]
        }
    }
]


# 3. EXECUTE TOOLS --> This the bridge between claude and python function(tools) 
def execute_tool(tool_name, tool_input):
    if tool_name == "get_order_details":
        return get_order_details(tool_input["order_id"])
    if tool_name == "get_refund_history":
        return get_refund_history(tool_input["user_id"])
    if tool_name == "check_delivery_status":
        return check_delivery_status(tool_input["tracking_number"],tool_input["carrier"])


# 4. AGENT LOOP -->This iterate until the loops task is done
def run_support_agent(user_message, conversation_id): # this function is to give the user message to the LLM 
    conv = Conversation.objects.get(id = conversation_id)

    conversation_messages = []

    for msg in conv.messages.order_by("created_at"):
        conversation_messages.append({
            "role" : msg.role,
            "content" : msg.content
        })

    # sen this conversation to LLM
    response = client.messages.create(
        model = model,
        max_tokens = 1024,
        system = SUUPORT_SYSYTEM_PROMPT,
        messages = conversation_messages
    )

    final_text = response.content[0].text

    return final_text