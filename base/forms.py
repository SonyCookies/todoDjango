from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Task

class TaskForm(ModelForm):
  class Meta:
    model = Task
    fields = ['title', 'description', 'due_date', 'completed', 'priority','category']

class UserForm(ModelForm):
  class Meta:
    model = User
    fields = ['username', 'email']