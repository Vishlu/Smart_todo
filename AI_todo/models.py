from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    usage_count = models.IntegerField(default=0)
    def __str__(self): return self.name

class ContextEntry(models.Model):
    SOURCE_CHOICES=[("whatsapp","WhatsApp"),("email","Email"),("note","Note")]
    content = models.TextField()
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="note")
    created_at = models.DateTimeField(default=timezone.now)
    processed_insights = models.JSONField(blank=True, null=True)
    def __str__(self): return f"{self.source_type} — {self.created_at:%Y-%m-%d %H:%M}"

class Task(models.Model):
    STATUS_CHOICES=[("pending","Pending"),("in_progress","In Progress"),("done","Done")]
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority_score = models.FloatField(default=0.0)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.title
