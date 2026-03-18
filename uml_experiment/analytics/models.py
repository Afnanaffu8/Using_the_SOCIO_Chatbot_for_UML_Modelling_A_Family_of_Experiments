from django.db import models
from django.conf import settings

class ExperimentReport(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Statistics
    total_participants = models.IntegerField(default=0)
    chatbot_participants = models.IntegerField(default=0)
    graphical_participants = models.IntegerField(default=0)
    
    # Performance metrics
    avg_time_chatbot = models.FloatField(null=True, blank=True)
    avg_time_graphical = models.FloatField(null=True, blank=True)
    avg_quality_chatbot = models.FloatField(null=True, blank=True)
    avg_quality_graphical = models.FloatField(null=True, blank=True)
    
    # Statistical analysis
    statistical_results = models.JSONField(null=True, blank=True)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    class Meta:
        db_table = 'experiment_reports'
        ordering = ['-generated_at']
    
    def __str__(self):
        return self.title
