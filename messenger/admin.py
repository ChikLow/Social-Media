from django.contrib import admin
from .models import Conversation, Message

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender','content','created_at')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id','participant_list','created_at')
    search_fields = ('participants__username',)
    inlines = (MessageInline,)

    def participant_list(self, obj):
        return ", ".join([u.username for u in obj.participants.all()])
    participant_list.short_description = 'Participants'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id','conversation','sender','is_read','created_at')
    list_filter = ('is_read','created_at')
    search_fields = ('sender__username','content')
