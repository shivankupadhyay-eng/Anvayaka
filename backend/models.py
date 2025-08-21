from django.db import models
from django.contrib.auth.models import User  # For owners and thekedars
from django.contrib.postgres.fields import ArrayField  # If using Postgres
import uuid 
from django.contrib.auth import get_user_model

User = get_user_model()

class Role(models.TextChoices):
    OWNER = 'owner', 'Owner'
    THEKEDAR = 'thekedar', 'Thekedar'

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,)
    role = models.CharField(max_length=20, choices=Role.choices)

    def __str__(self):
        return self.user.username

class Labour(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    expertise = ArrayField(models.CharField(max_length=100), blank=False)  # e.g., ['welding', 'assembly']
    alias = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Stock(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)  # e.g., 'raw material', 'tool'
    quantity = models.DecimalField(max_digits=10, decimal_places=2)  # For precise quantities, e.g., kg, units
    unit = models.CharField(max_length=50, default='units')  # Clarify 'pda hua maal' as unit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class Task(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('complete', 'Complete'),
        ('overdue', 'Overdue'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running')
    quantity = models.PositiveIntegerField()  
    completed_quantity = models.PositiveIntegerField(default=0)  
    due_date = models.DateField()
    labour = models.ForeignKey(Labour, related_name='assigned_tasks', on_delete=models.SET_NULL, null=True)  # Owner assigns
    thekedar = models.ForeignKey(UserProfile, related_name='owned_tasks', on_delete=models.SET_NULL, null=True)  # Assigned to thekedar
    stocks = models.ManyToManyField(Stock, related_name='tasks', blank=False)  # Stocks provided for this task
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def progress(self):        
        if self.quantity > 0:
            return (self.completed_quantity / self.quantity) * 100
        return 0

    def __str__(self):
        return self.name

class Parchi(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, related_name='parchis', on_delete=models.CASCADE)
    labour = models.ForeignKey(Labour, related_name='parchis', on_delete=models.CASCADE)
    details = models.TextField(blank=False)  # Formerly 'perchi detail'
    deliverable = models.PositiveIntegerField()  # Quantity this labour must produce
    deadline = models.DateField()  # Can be task's due_date by default
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Parchi for {self.labour.name} on {self.task.name}"