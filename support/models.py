from django.db import models
from django.contrib.auth.models import User
from orders.models import Order


# Suuport App with COnversation and message

# -------------------------
# CONVERSATION MODELS
# -------------------------
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="conversations")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} by {self.user.username} / Order {self.order.id}"



# -------------------------
# MESSAGE MODELS
# -------------------------
class Message(models.Model):

    ROLE_CHOICES = [
        ("user", "User"),
        ("agent", "Agent"),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} in Conversation {self.content[:50]} by {self.role}"