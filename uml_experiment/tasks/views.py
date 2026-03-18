from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task, TaskAssignment

@login_required
def my_tasks(request):
    if request.user.is_admin:
        return redirect('adminpanel:task_list')
    
    assignments = TaskAssignment.objects.filter(
        user=request.user
    ).select_related('task').order_by('-assigned_at')
    
    context = {'assignments': assignments}
    return render(request, 'tasks/my_tasks.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    try:
        assignment = TaskAssignment.objects.get(user=request.user, task=task)
    except TaskAssignment.DoesNotExist:
        messages.error(request, 'This task is not assigned to you.')
        return redirect('tasks:my_tasks')
    
    context = {
        'task': task,
        'assignment': assignment
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def start_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    try:
        assignment = TaskAssignment.objects.get(user=request.user, task=task)
    except TaskAssignment.DoesNotExist:
        messages.error(request, 'This task is not assigned to you.')
        return redirect('tasks:my_tasks')
    
    if assignment.status == 'completed':
        messages.info(request, 'You have already completed this task.')
        return redirect('submissions:detail', pk=assignment.submission.pk)
    
    # Redirect to appropriate tool
    if task.tool_type == 'chatbot':
        return redirect('chatbot:interface', assignment_id=assignment.pk)
    else:
        return redirect('graphical_tool:interface', assignment_id=assignment.pk)
