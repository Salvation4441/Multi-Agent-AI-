from support.event_queue import publish,DONE
from anthropic import Anthropic
from django.conf import settings
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from .langchain_tools import get_order_details, get_refund_history, check_delivery_status, search_knowledge_base
from langgraph.checkpoint.memory import InMemorySaver
from .models import AgentLog, Conversation
from langchain.agents.middleware import wrap_tool_call


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
        tools= SUPPORT_TOOLS,
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