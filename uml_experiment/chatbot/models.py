from django.db import models
from django.conf import settings
from tasks.models import TaskAssignment

class ChatSession(models.Model):
    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='chat_session')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    diagram_data = models.JSONField(null=True, blank=True)
    message_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Chat Session {self.session_id}"


class ChatMessage(models.Model):
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
    )
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    diagram_snapshot = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"
