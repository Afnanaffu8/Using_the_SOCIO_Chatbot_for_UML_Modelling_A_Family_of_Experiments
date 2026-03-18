from django.db import models
from django.conf import settings

class Task(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )
    
    TOOL_TYPE_CHOICES = (
        ('chatbot', 'Chatbot'),
        ('graphical', 'Graphical Tool'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Detailed requirements for the UML diagram")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    tool_type = models.CharField(max_length=20, choices=TOOL_TYPE_CHOICES)
    expected_classes = models.IntegerField(help_text="Expected number of classes")
    expected_relationships = models.IntegerField(help_text="Expected number of relationships")
    time_limit = models.IntegerField(help_text="Time limit in minutes", default=30)
    sample_solution = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['difficulty', 'title']
    
    def __str__(self):
        return f"{self.title} ({self.get_tool_type_display()})"


class TaskAssignment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    time_taken = models.IntegerField(null=True, blank=True, help_text="Time taken in seconds")
    
    class Meta:
        db_table = 'task_assignments'
        unique_together = ('user', 'task')
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title}"
