from django.db import models
from tasks.models import TaskAssignment

class DiagramSession(models.Model):
    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='diagram_session')
    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    last_saved = models.DateTimeField(auto_now=True)
    diagram_data = models.JSONField(default=dict)
    action_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'diagram_sessions'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Diagram Session {self.session_id}"


class DiagramAction(models.Model):
    ACTION_TYPE_CHOICES = (
        ('add_class', 'Add Class'),
        ('edit_class', 'Edit Class'),
        ('delete_class', 'Delete Class'),
        ('add_relationship', 'Add Relationship'),
        ('edit_relationship', 'Edit Relationship'),
        ('delete_relationship', 'Delete Relationship'),
        ('move_element', 'Move Element'),
    )
    
    session = models.ForeignKey(DiagramSession, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPE_CHOICES)
    action_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'diagram_actions'
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.action_type} at {self.timestamp}"
