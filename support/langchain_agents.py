from support.agents import MANAGER_SYSYTEM_PROMPT
from support.event_queue import publish,DONE
from anthropic import Anthropic
from django.conf import settings
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .langchain_tools import get_order_details, get_refund_history, check_delivery_status, search_knowledge_base
from langgraph.checkpoint.memory import InMemorySaver
from .models import AgentLog, Conversation
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool


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



# Initialize Anthropic client
llm = ChatAnthropic(model = settings.CLAUDE_MODEL,api_key = settings.CLAUDE_API_KEY)

# Support tools
SUPPORT_TOOLS = [get_order_details, get_refund_history, check_delivery_status, search_knowledge_base]




# checkpointer
checkpointer = InMemorySaver()


# running agent
def run_support_langchain_agent(user_message, conversation_id, order_id, user_id):
    convo = Conversation.objects.get(id = conversation_id)

    
    config = {"configurable": {"thread_id":str(conversation_id)}}

    contextual_message = f"[Context: This conversation is about Order #{order_id}, user: {user_id}] {user_message}"

    @tool
    def escalate_to_manager(case_summary: str) -> dict:
        """Escalate the case to the manager for a refund decision, Use this when customer request a refund or compensation. Prepare a detailed summary of the case including refund history,order details and customer complaints before escalating"""
        return run_manager_langchain_agent(case_summary,conversation_id)


    # MiddleWare
    @wrap_tool_call
    def log_tool_call_middleware(request, handler):
        tool_name = request.tool_call["name"]
        tool_args = request.tool_call['args']


        #  before tool call - publishing
        event = {"type":"tool_call","message":f"Tool Call {tool_name} with {tool_args}"}
        publish(conversation_id,event)
        

        # before tool execution
        AgentLog.objects.create(
            conversation=convo,
            event_type="tool_call",
            message=f"Tool Call {tool_name} with {tool_args}"
        )
        
        result = handler(request) # tool execution

        # after tool execution
        #  after tool call - publishing
        event = {"type":"tool_result","message":f"{tool_name} returned:  {str(result.content)[:200]}"}
        publish(conversation_id,event)


        

        # store log result after executing
        AgentLog.objects.create(
            conversation=convo,
            event_type="tool_result",
            message=f"Tool Result {tool_name} with {str(result.content)[:200]}"
        )

        return result



    # Agent
    support_agent = create_agent(
        model = llm,
        tools= SUPPORT_TOOLS + [escalate_to_manager],
        system_prompt= SUPPORT_SYSTEM_PROMPT,
        checkpointer= checkpointer,
        middleware=[log_tool_call_middleware],
    )

    result = support_agent.invoke({"messages": [{"role": "user", "content": contextual_message}]}, config=config)

    reply = result["messages"][-1].content


    #  final reponse - publishing
    event = {"type":"final","message":str(reply)}
    publish(conversation_id,event)

    # save final reply to the AgentLog
    AgentLog.objects.create(    
        conversation = convo,
        event_type="final",
        message = reply,
    )

    publish(conversation_id,DONE)

    
    return reply


# manager agent
def run_manager_langchain_agent(case_summary, conversation_id):
    convo  = Conversation.objects.get(id = conversation_id)

    event = {"type":"manager","message":f"Case recieved for review {case_summary[:200]}"}
    publish(conversation_id,event)

    AgentLog.objects.create(conversation = convo,event_type="manager",message = f"Case recieved for review {case_summary[:200]}")

    # creating the agent
    manager_agent = create_agent(
        model = llm,
        system_prompt=MANAGER_SYSYTEM_PROMPT,
        tools=[],
    )


    result = manager_agent.invoke({"messages":[{"role" : "user","content":case_summary}]})

    decision = result["messages"][-1].content


    # publish decision
    event = {"type":"decision","message":str(decision[:200])}
    publish(conversation_id,event)


    # store in AgentLog
    AgentLog.objects.create(conversation = convo, event_type="manager",message=f"Manager Decision: {decision[:200]}")

    return decision