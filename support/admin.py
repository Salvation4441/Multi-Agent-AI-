from django.contrib import admin
from .models import AgentLog, Conversation, Message


class ConversationAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "order", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "order__id"]
    raw_id_fields = ["user", "order"]
    date_hierarchy = "created_at"


class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "conversation", "role", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["content", "role", "conversation__user__username"]
    raw_id_fields = ["conversation"]
    date_hierarchy = "created_at"


class AgentLogAdmin(admin.ModelAdmin):
    list_display = ["id", "conversation", "event_type", "created_at"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["message", "event_type", "conversation__user__username"]
    raw_id_fields = ["conversation"]
    date_hierarchy = "created_at"


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(AgentLog, AgentLogAdmin)