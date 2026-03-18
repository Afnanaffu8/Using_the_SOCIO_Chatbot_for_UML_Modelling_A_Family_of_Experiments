from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('participant', 'Participant'),
        ('admin', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='participant')
    participant_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    uml_experience = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_participant(self):
        return self.user_type == 'participant'
