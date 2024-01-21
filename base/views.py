from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TaskForm, UserForm
from .models import Task, Category
from django.db.models import Q
from django.http import HttpResponse



def home(request):
  return render(request, 'base/home.html')

# Create your views here.
@login_required(login_url='login')
def index(request):
  user = request.user
  q = request.GET.get('q') if request.GET.get('q') is not None else ''
  sort_param = request.GET.get('sort')

  categories = Category.objects.all()

  tasks = user.task_set.filter(
    Q(category__name__icontains=q) |
    Q(title__icontains=q),
    completed=False
  )

  tasks_completed = user.task_set.filter(
    Q(category__name__icontains=q) |
    Q(title__icontains=q),
    completed=True
  )

  tasks_completed = tasks_completed.order_by('-updated')

  # Set default sorting to 'priority' if no sort_param is provided
  if not sort_param:
    sort_param = 'priority'

  # Apply sorting based on the sort_param
  if sort_param == 'hpriority':
    tasks = tasks.order_by('priority', 'created')
  elif sort_param == 'lpriority':
    tasks = tasks.order_by('-priority', 'created')
  elif sort_param == 'fcreated':
    tasks = tasks.order_by('created')
  elif sort_param == 'lcreated':
    tasks = tasks.order_by('-created')
  else:
    # Default sorting if no sort_param is provided
    tasks = tasks.order_by('created')

  category_count = Category.objects.all().count()

  task_count = tasks.count()
  context = {'tasks': tasks, 'category_count': category_count, 
             'categories': categories, 'task_count': task_count, 
             'sort_param': sort_param, 'user': user, 'tasks_completed': tasks_completed}
  return render(request, 'base/index.html', context)


def loginPage(request):
  page = 'login'

  if request.user.is_authenticated:
    return redirect('index')

  if request.method == 'POST':
    username = request.POST.get('username').lower()
    password = request.POST.get('password')
    
    try:
      user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist: 
      messages.error(request, 'User does not exist.')
      return render(request, 'base/login_register.html', {'page': page})

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)
      return redirect('index')
    else:
      messages.error(request, 'Password incorrect')
      
  context = {'page': page}
  return render(request, 'base/login_register.html', context)

def logoutUser(request):
  logout(request)
  return redirect('login')

def registerPage(request):
  page = 'register'
  form = UserCreationForm()

  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save(commit=False)
      user.username = user.username.lower()
      user.save()
      login(request, user)
      return redirect('home')
    else: 
      messages.error(request, 'Failed to create an account.')

  context = {'page': page, 'form': form}
  return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def addTask(request):
  form = TaskForm()
  categories = Category.objects.all()
  if request.method == 'POST':
    category_name = request.POST.get('category')
    category, created = Category.objects.get_or_create(name=category_name)

    Task.objects.create(
      user=request.user,
      category = category,
      title=request.POST.get('title'),
      description=request.POST.get('description'),
      priority=request.POST.get('priority')
    )
    return redirect('index')
  
  context = {'form': form, 'categories': categories}
  return render(request, 'base/tasks_form.html', context)

@login_required(login_url='login')
def updateTask(request, pk):
  task = Task.objects.get(id=pk)
  form = TaskForm(instance=task)
  categories = Category.objects.all()

  if request.user != task.user:
    return HttpResponse('You are not allowed here!!')
  
  if request.method == 'POST':
    category_name = request.POST.get('category')
    category, created = Category.objects.get_or_create(name=category_name)
    task.title = request.POST.get('title')
    task.category = category
    task.description = request.POST.get('description')
    task.priority = request.POST.get('priority')
    task.save()
    return redirect('index')

  context = {'task': task, 'form': form, 'categories': categories}
  return render(request, 'base/tasks_form.html', context)

def deleteTask(request, pk):
  task = Task.objects.get(id=pk)

  if request.user != task.user:
    return HttpResponse('You are not allowed here!!')

  if request.method == 'POST':
    task.delete()
    return redirect('index')

  context = {'task': task, 'obj': task}
  return render(request, 'base/task_action.html', context)

def doneTask(request, pk):
  task = Task.objects.get(id=pk)

  if request.user != task.user:
    return HttpResponse('You are not allowed here!!')
  
  if request.method == 'POST':
    task.completed = True
    task.save()
    return redirect('index')
  
  context = {'task': task}
  return render(request, 'base/task_action.html', context)

def userProfile(request):
  user = request.user

  tasks = user.task_set.filter(
    completed=False
  )

  tasks_completed = user.task_set.filter(
    completed=True
  )

  categories = Category.objects.all()

  tasks_completed = tasks_completed.order_by('-updated')


  context = {'user': user, 'tasks': tasks, 'tasks_completed': tasks_completed, 'categories': categories}
  return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def updateUser(request):
  user = request.user
  form = UserForm(instance=user)

  if request.method == "POST":
    form = UserForm(request.POST, instance=user)
    if form.is_valid():
      form.save()
      return redirect('profile')

  context = {'form': form}
  return render(request, 'base/update-user.html', context)

def categoriesPage(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''  # searching
    categories = Category.objects.filter(name__icontains=q)
    context = {'categories': categories}
    return render(request, 'base/categories.html', context)


def activityPage(request):
  user = request.user
  tasks_completed = user.task_set.filter(
    completed=True
  )
  tasks_completed = tasks_completed.order_by('-updated')

  context = {'tasks_completed': tasks_completed}
  return render(request, 'base/activity.html', context)