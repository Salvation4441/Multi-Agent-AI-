from django.shortcuts import render
import json
from django.http import JsonResponse
import time

# Create your views here.
def chat(request, order_id):
    if request.method == "POST":
        data = json.loads(request.body)
        user_messgae = data.get("message")

        if not user_messgae:
            return JsonResponse({"error" : "Empty message"}, status=400)
        
        time.sleep(3);
        return JsonResponse({"reply" : "here is the reply"})
