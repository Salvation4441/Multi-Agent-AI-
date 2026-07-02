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
"""

# MANGER SYSTEM PROMPT
MANAGER_SYSYTEM_PROMPT ="""
You are a senior manager at CoolBreeze AC.
A support agent has escalated a customer case to you for a refund decision.

Your responsibilities:
- Review the case summary carefully
- Consider the customer's refund history
- Decide whether to approve or deny the refund
- Communicate your decision clearly
- Make a fair and final refund decision
- Give a clear reason for your decision


Your decision option:
- Approve refund - if the case is genuine and within policy
- Deny refund - if the case is suspicious or outside policy
- Escalate - if you suspect  fraud or policy violation


Important rules:
- Be fair but firm and objective
- Base decision on facts not emotions
- Always give a speicic reasonfor your decision
- Keep your response concise and professional

"""

# RISK AGENT SYSTEM PROMPT
RISK_SYSTEM_PROMPT = """
You are a fraud risk analyst at CoolBreeze AC.
A support manager has sent you a customer profile for risk assessment.

Your job:
- Analyse the customer's order and refund patterns
- Identify suspicious behaviour
- Return a clear risk verdict

Risk levels:
- LOW — genuine customer, normal behaviour
- MEDIUM — some suspicious signals, proceed with caution
- HIGH — clear fraud pattern, recommend denial

Your response format:
- Risk Level: LOW / MEDIUM / HIGH
- Key Signals: what you found suspicious or genuine
- Recommendation: what manager should do

Important:
- Be objective — base verdict on data only
- One bad refund does not make someone fraudulent
- Look for patterns — not isolated incidents
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
                   "description" : "The order ID to look up"
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
    },


    # ecalate to manager
    {
        "name" : "escalate_to_manager",
        "description" : "Escalate the case to the manager for a refund decision, Use this when customer request a refund or compensation. Prepare a detailed summary of the case including refund history,order details and customer complaints before escalating",
        "input_schema":{
            "type" : "object",
            "properties" : {
                "case_summary":{
                    "type" : "string",
                    "description" : "Complete case summary including order details, refund history,customer complaints and current conversation"
                }
            },
            "required":["case_summary"]
        }
    }
]



# RISK AGENT ----> Tool schema
RISK_TOOLS = [
    {
        "name": "get_customer_risk_profile",
        "description" : "Get the risk profile of a customer including order history,refund history,refund patterns and ratio. Use this to asses fraud risk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "The user ID to check the risk profile of"
                }
            },
            "required": ["user_id"]
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
    if tool_name == "escalate_to_manager":
        case_summary = tool_input["case_summary"]
        print("Case Summary\n\n",case_summary)
        decision = run_manager_agent(case_summary)
        print("Decision\n\n",decision)
        return decision


# 4. AGENT LOOP -->This iterate until the loops task is done
def run_support_agent(user_message, conversation_id, order_id,user_id): # this function is to give the user message to the LLM 
    conv = Conversation.objects.get(id = conversation_id)

    conversation_messages = []

    for msg in conv.messages.order_by("created_at"):
        conversation_messages.append({
            "role" : msg.role,
            "content" : msg.content
        })

    while True:
        # sen this conversation to LLM
        response = client.messages.create(
            model = model,
            max_tokens = 1024,
            system = SUUPORT_SYSYTEM_PROMPT + f"\n\nContext: This conversation is about Order # {order_id}, user: {user_id}",
            tools=SUPPORT_TOOLS, # putting the support functions here
            messages = conversation_messages
        )

        # print('Stop Reson ==>', response.stop_reason)
        # print('Content ==>',response.content)

        if response.stop_reason == 'tool_use':
            # store the tool use blocks
            tool_results = []

            for block in response.content:
                if block.type == 'tool_use':
                    # print('Tool Call ==>',block.name)
                    # print('Tool Input ==>',block.input)

                    
                    # execute the tool
                    result = execute_tool(block.name, block.input)
                    # print('Tool Result ==>', result)


                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id" : block.id,
                        "content" : str(result)
                    })
            
            conversation_messages.append({
                "role" : "assistant",
                "content" : response.content,
            })

            conversation_messages.append({
                "role" : "user",
                "content" : tool_results
            })
        
        else:
            return response.content[0].text


# 5. MANAGER LOOP
def run_manager_agent(case_summary):
    manager_messages = [
        {
            'role':'user', #user is the task giver
            'content' : case_summary
        }
    ]

    while True:
        response = client.messages.create(
            model = model,
            max_tokens=1024,
            system = MANAGER_SYSYTEM_PROMPT,
            messages = manager_messages
        )

        if response.stop_reason == 'tool_use':
            tool_results = []
            for block in response.content:
                if block.type == 'tool_use':
                    # execute the tool 
                    result = execute_tool(block.name,block.input)
                    
                    tool_results.append({
                        'type': 'tool_use',
                        'tool_use_id' : block.id,
                        'content' : result
                    })
            manager_messages.append({
                'role' : 'assistant',
                'content' : response.content
            })

            manager_messages.append({
                'role' : 'user',
                'content': tool_results
            })
        else:
            return response.content[0].text