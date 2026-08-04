from django.shortcuts import render,get_object_or_404
import json
from django.http import JsonResponse,StreamingHttpResponse
import time
from .models import *
from support.agents import run_support_agent
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .event_queue import subscribe, unsubscribe, publish




@login_required
def chat(request, order_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")

        if not user_message:
            return JsonResponse({"error" : "Empty message"}, status=400)
        
        order = get_object_or_404(Order, id = order_id, user = request.user)

        conversation, created = Conversation.objects.get_or_create(user = request.user, order=order)

        # store the message
        Message.objects.create(conversation = conversation, role="user", content= user_message)

        # send user message and conversation LLM
        reply = run_support_agent(user_message, conversation.id, order.id,request.user.id)

        # store the LLM reply
        Message.objects.create(conversation=conversation, role="assistant", content = reply)

        
        # time.sleep(5);
        return JsonResponse({"reply" : reply})



@staff_member_required
def dashboard(request):
    # display all the conversation list
    conversations = Conversation.objects.all().order_by('-created_at')

    context ={
        "conversations" : conversations,
    }

    return render(request,'support/dashboard.html',context)




# Conversations
@staff_member_required
def conversation_details(request,conversation_id):
    conversation = get_object_or_404(Conversation, id = conversation_id)
    messages = conversation.messages.order_by('created_at')
    agentlogs = conversation.agentlogs.order_by('created_at')

    context ={
        "conversation" : conversation,
        "messages" : messages,
        "agentlogs" : agentlogs,
    }
    return render(request, 'support/conversation_detail.html', context)



# Conversation Stream
@staff_member_required
def conversation_stream(request, conversation_id):
    # yield keyword make a function become a generated function
    # generator function used for streaming SSE
    #  generated function will give u you the response chunk by chunk

    def event_stream(conversation_id):
        q = subscribe(conversation_id)

        try:
            while True:
                event = q.get() # this will wait for the next event
                # if event is DONE:
                #     break
                yield f"data: {json.dumps(event)}\n\n"
        finally:
            unsubscribe(conversation_id, q)

    return StreamingHttpResponse(event_stream(conversation_id),content_type="text/event-stream")