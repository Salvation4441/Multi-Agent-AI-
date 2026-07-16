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
    pass


def publish(conversation_id, event):
    pass