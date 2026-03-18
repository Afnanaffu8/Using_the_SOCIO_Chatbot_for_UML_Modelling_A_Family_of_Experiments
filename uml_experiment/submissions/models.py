from django.db import models
from django.conf import settings
from tasks.models import TaskAssignment

class Submission(models.Model):
    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='submission')
    submitted_at = models.DateTimeField(auto_now_add=True)
    diagram_data = models.JSONField()
    diagram_image = models.ImageField(upload_to='submissions/', null=True, blank=True)
    
    # Automated metrics
    class_count = models.IntegerField(default=0)
    relationship_count = models.IntegerField(default=0)
    attribute_count = models.IntegerField(default=0)
    method_count = models.IntegerField(default=0)
    
    # Quality scores
    completeness_score = models.FloatField(null=True, blank=True)
    correctness_score = models.FloatField(null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    
    # Admin evaluation
    admin_notes = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)
    evaluated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Submission by {self.assignment.user.username}"


class Feedback(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='feedback')
    ease_of_use = models.IntegerField(help_text="Rating 1-5")
    satisfaction = models.IntegerField(help_text="Rating 1-5")
    efficiency = models.IntegerField(help_text="Rating 1-5")
    would_recommend = models.BooleanField()
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback'
    
    def __str__(self):
        return f"Feedback for {self.submission}"
