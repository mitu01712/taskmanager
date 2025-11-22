from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date, timedelta
from .models import Task
from .forms import TaskForm, UserRegisterForm

# Registration View
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_list')
    else:
        form = UserRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

# Task List (With Search & Filter)
@login_required
def task_list(request):
   
    tasks = Task.objects.filter(owner=request.user)

    # Search Logic
    search_query = request.GET.get('search')
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )

    # Filtering Logic
    status_filter = request.GET.get('status')
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    priority_filter = request.GET.get('priority')
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    # Date Filtering
    due_date_filter = request.GET.get('due_date')
    today = date.today()
    if due_date_filter == 'today':
        tasks = tasks.filter(due_date=today)
    elif due_date_filter == 'this_week':
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        tasks = tasks.filter(due_date__range=[start_week, end_week])
    elif due_date_filter == 'overdue':
        tasks = tasks.filter(due_date__lt=today, status__in=['Pending', 'In Progress'])

    # Sorting
    sort_by = request.GET.get('sort')
    if sort_by == 'oldest':
        tasks = tasks.order_by('created_at')
    else:
        tasks = tasks.order_by('-created_at') # Default newest

    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# Create Task
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user 
            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

# Task Detail
@login_required
def task_detail(request, pk):
   
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})

# Update Task
@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Update Task'})

# Delete Task
@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, owner=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})