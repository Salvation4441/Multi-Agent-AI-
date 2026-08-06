import queue

# who is watching what conversation

subscribers = {} #{25: [queue1,queue2,queue3]}

def subscribe(conversation_id):
    q = queue.Queue() #creating an empty queue instance

    # check if the conversation has no subscribers yet
    if conversation_id not in subscribers:
        subscribers[conversation_id] = [] #initialise an empty list for this conversation
   
    subscribers[conversation_id].append(q)  # now add the new queue to the list of subscribers

    return q



def unsubscribe(conversation_id, queue):
    if conversation_id in subscribers:
        subscribers[conversation_id].remove(queue)
        # if this was the last subscriber, remove the conversation from the dict
        if not subscribers[conversation_id]:
            del subscribers[conversation_id]




def publish(conversation_id, event):
    if conversation_id in subscribers:
        for q in subscribers[conversation_id]:
            q.put(event)
        

    # Sentinel value it tells the SSE(Server Sent Event) connection to stop or close
DONE = {"type": "done"}