from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from accounts.models import User
from tasks.models import Task, TaskAssignment
from submissions.models import Submission, Feedback
from django.utils import timezone
import random
import string

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('accounts:dashboard')
    
    # Statistics
    total_participants = User.objects.filter(user_type='participant').count()
    total_tasks = Task.objects.count()
    total_assignments = TaskAssignment.objects.count()
    completed_assignments = TaskAssignment.objects.filter(status='completed').count()
    
    # Recent submissions
    recent_submissions = Submission.objects.select_related(
        'assignment__user', 'assignment__task'
    ).order_by('-submitted_at')[:5]
    
    # Performance metrics
    avg_completion_time = TaskAssignment.objects.filter(
        status='completed', time_taken__isnull=False
    ).aggregate(Avg('time_taken'))['time_taken__avg']
    
    context = {
        'total_participants': total_participants,
        'total_tasks': total_tasks,
        'total_assignments': total_assignments,
        'completed_assignments': completed_assignments,
        'recent_submissions': recent_submissions,
        'avg_completion_time': avg_completion_time,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
def participant_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    participants = User.objects.filter(user_type='participant').annotate(
        total_tasks=Count('assignments'),
        completed_tasks=Count('assignments', filter=Q(assignments__status='completed'))
    ).order_by('-created_at')
    
    context = {'participants': participants}
    return render(request, 'adminpanel/participant_list.html', context)

@login_required
def add_participant(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        age = request.POST.get('age')
        education_level = request.POST.get('education_level')
        uml_experience = request.POST.get('uml_experience')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'adminpanel/add_participant.html')
        
        # Generate participant ID
        participant_id = f"P{''.join(random.choices(string.digits, k=6))}"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='participant',
            participant_id=participant_id,
            age=age,
            education_level=education_level,
            uml_experience=uml_experience
        )
        
        messages.success(request, f'Participant {username} created successfully!')
        return redirect('adminpanel:participant_list')
    
    return render(request, 'adminpanel/add_participant.html')

@login_required
def edit_participant(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    participant = get_object_or_404(User, pk=pk, user_type='participant')
    
    if request.method == 'POST':
        participant.email = request.POST.get('email')
        participant.age = request.POST.get('age')
        participant.education_level = request.POST.get('education_level')
        participant.uml_experience = request.POST.get('uml_experience')
        participant.save()
        
        messages.success(request, 'Participant updated successfully!')
        return redirect('adminpanel:participant_list')
    
    context = {'participant': participant}
    return render(request, 'adminpanel/edit_participant.html', context)

@login_required
def delete_participant(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    participant = get_object_or_404(User, pk=pk, user_type='participant')
    
    if request.method == 'POST':
        username = participant.username
        participant.delete()
        messages.success(request, f'Participant {username} deleted successfully!')
        return redirect('adminpanel:participant_list')
    
    context = {'participant': participant}
    return render(request, 'adminpanel/delete_participant.html', context)

@login_required
def task_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    tasks = Task.objects.annotate(
        assignment_count=Count('assignments')
    ).order_by('-created_at')
    
    context = {'tasks': tasks}
    return render(request, 'adminpanel/task_list.html', context)

@login_required
def add_task(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        task = Task.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            difficulty=request.POST.get('difficulty'),
            tool_type=request.POST.get('tool_type'),
            expected_classes=request.POST.get('expected_classes'),
            expected_relationships=request.POST.get('expected_relationships'),
            time_limit=request.POST.get('time_limit', 30),
        )
        
        messages.success(request, f'Task "{task.title}" created successfully!')
        return redirect('adminpanel:task_list')
    
    return render(request, 'adminpanel/add_task.html')

@login_required
def edit_task(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.requirements = request.POST.get('requirements')
        task.difficulty = request.POST.get('difficulty')
        task.tool_type = request.POST.get('tool_type')
        task.expected_classes = request.POST.get('expected_classes')
        task.expected_relationships = request.POST.get('expected_relationships')
        task.time_limit = request.POST.get('time_limit')
        task.is_active = request.POST.get('is_active') == 'on'
        task.save()
        
        messages.success(request, 'Task updated successfully!')
        return redirect('adminpanel:task_list')
    
    context = {'task': task}
    return render(request, 'adminpanel/edit_task.html', context)

@login_required
def experiment_config(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    return render(request, 'adminpanel/experiment_config.html')

@login_required
def assignment_management(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        participant_ids = request.POST.getlist('participants')
        task_id = request.POST.get('task')
        
        task = get_object_or_404(Task, pk=task_id)
        created_count = 0
        
        for participant_id in participant_ids:
            participant = User.objects.get(pk=participant_id)
            assignment, created = TaskAssignment.objects.get_or_create(
                user=participant,
                task=task,
                defaults={'status': 'pending'}
            )
            if created:
                created_count += 1
        
        messages.success(request, f'{created_count} assignments created successfully!')
        return redirect('adminpanel:assignment_management')
    
    participants = User.objects.filter(user_type='participant')
    tasks = Task.objects.filter(is_active=True)
    assignments = TaskAssignment.objects.select_related('user', 'task').order_by('-assigned_at')[:20]
    
    context = {
        'participants': participants,
        'tasks': tasks,
        'assignments': assignments,
    }
    return render(request, 'adminpanel/assignment_management.html', context)

@login_required
def submission_review(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    submissions = Submission.objects.select_related(
        'assignment__user', 'assignment__task'
    ).order_by('-submitted_at')
    
    context = {'submissions': submissions}
    return render(request, 'adminpanel/submission_review.html', context)

@login_required
def evaluate_submission(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        submission.completeness_score = request.POST.get('completeness_score')
        submission.correctness_score = request.POST.get('correctness_score')
        submission.quality_score = request.POST.get('quality_score')
        submission.admin_notes = request.POST.get('admin_notes')
        submission.evaluated_by = request.user
        submission.evaluated_at = timezone.now()
        submission.save()
        
        messages.success(request, 'Submission evaluated successfully!')
        return redirect('adminpanel:submission_review')
    
    context = {'submission': submission}
    return render(request, 'adminpanel/evaluate_submission.html', context)
