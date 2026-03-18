from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from accounts.models import User
from tasks.models import Task, TaskAssignment
from submissions.models import Submission, Feedback
from .models import ExperimentReport
from scipy import stats
import pandas as pd
import json

@login_required
def analytics_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    # Overall statistics
    total_participants = User.objects.filter(user_type='participant').count()
    total_submissions = Submission.objects.count()
    
    # Tool-based statistics
    chatbot_submissions = Submission.objects.filter(
        assignment__task__tool_type='chatbot'
    ).count()
    
    graphical_submissions = Submission.objects.filter(
        assignment__task__tool_type='graphical'
    ).count()
    
    # Average metrics by tool type
    chatbot_metrics = Submission.objects.filter(
        assignment__task__tool_type='chatbot',
        assignment__time_taken__isnull=False
    ).aggregate(
        avg_time=Avg('assignment__time_taken'),
        avg_classes=Avg('class_count'),
        avg_relationships=Avg('relationship_count'),
        avg_completeness=Avg('completeness_score')
    )
    
    graphical_metrics = Submission.objects.filter(
        assignment__task__tool_type='graphical',
        assignment__time_taken__isnull=False
    ).aggregate(
        avg_time=Avg('assignment__time_taken'),
        avg_classes=Avg('class_count'),
        avg_relationships=Avg('relationship_count'),
        avg_completeness=Avg('completeness_score')
    )
    
    # Feedback averages
    chatbot_feedback = Feedback.objects.filter(
        submission__assignment__task__tool_type='chatbot'
    ).aggregate(
        avg_ease=Avg('ease_of_use'),
        avg_satisfaction=Avg('satisfaction'),
        avg_efficiency=Avg('efficiency')
    )
    
    graphical_feedback = Feedback.objects.filter(
        submission__assignment__task__tool_type='graphical'
    ).aggregate(
        avg_ease=Avg('ease_of_use'),
        avg_satisfaction=Avg('satisfaction'),
        avg_efficiency=Avg('efficiency')
    )
    
    context = {
        'total_participants': total_participants,
        'total_submissions': total_submissions,
        'chatbot_submissions': chatbot_submissions,
        'graphical_submissions': graphical_submissions,
        'chatbot_metrics': chatbot_metrics,
        'graphical_metrics': graphical_metrics,
        'chatbot_feedback': chatbot_feedback,
        'graphical_feedback': graphical_feedback,
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required
def performance_metrics(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    # Get all submissions with related data
    submissions = Submission.objects.select_related(
        'assignment__user',
        'assignment__task'
    ).prefetch_related('feedback').all()
    
    # Group data by tool type
    chatbot_data = []
    graphical_data = []
    
    for sub in submissions:
        data_point = {
            'participant': sub.assignment.user.username,
            'task': sub.assignment.task.title,
            'time_taken': sub.assignment.time_taken or 0,
            'class_count': sub.class_count,
            'relationship_count': sub.relationship_count,
            'completeness_score': sub.completeness_score or 0,
        }
        
        if hasattr(sub, 'feedback'):
            data_point.update({
                'ease_of_use': sub.feedback.ease_of_use,
                'satisfaction': sub.feedback.satisfaction,
                'efficiency': sub.feedback.efficiency,
            })
        
        if sub.assignment.task.tool_type == 'chatbot':
            chatbot_data.append(data_point)
        else:
            graphical_data.append(data_point)
    
    context = {
        'chatbot_data': chatbot_data,
        'graphical_data': graphical_data,
    }
    return render(request, 'analytics/performance.html', context)

@login_required
def tool_comparison(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    # Get completion times
    chatbot_times = list(Submission.objects.filter(
        assignment__task__tool_type='chatbot',
        assignment__time_taken__isnull=False
    ).values_list('assignment__time_taken', flat=True))
    
    graphical_times = list(Submission.objects.filter(
        assignment__task__tool_type='graphical',
        assignment__time_taken__isnull=False
    ).values_list('assignment__time_taken', flat=True))
    
    # Statistical comparison
    statistical_results = {}
    
    if len(chatbot_times) > 0 and len(graphical_times) > 0:
        # T-test for completion time
        t_stat, p_value = stats.ttest_ind(chatbot_times, graphical_times)
        statistical_results['time_comparison'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    # Get quality scores
    chatbot_quality = list(Submission.objects.filter(
        assignment__task__tool_type='chatbot',
        completeness_score__isnull=False
    ).values_list('completeness_score', flat=True))
    
    graphical_quality = list(Submission.objects.filter(
        assignment__task__tool_type='graphical',
        completeness_score__isnull=False
    ).values_list('completeness_score', flat=True))
    
    if len(chatbot_quality) > 0 and len(graphical_quality) > 0:
        # T-test for quality
        t_stat, p_value = stats.ttest_ind(chatbot_quality, graphical_quality)
        statistical_results['quality_comparison'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    # Satisfaction comparison
    chatbot_satisfaction = list(Feedback.objects.filter(
        submission__assignment__task__tool_type='chatbot'
    ).values_list('satisfaction', flat=True))
    
    graphical_satisfaction = list(Feedback.objects.filter(
        submission__assignment__task__tool_type='graphical'
    ).values_list('satisfaction', flat=True))
    
    if len(chatbot_satisfaction) > 0 and len(graphical_satisfaction) > 0:
        # T-test for satisfaction
        t_stat, p_value = stats.ttest_ind(chatbot_satisfaction, graphical_satisfaction)
        statistical_results['satisfaction_comparison'] = {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'significant': p_value < 0.05
        }
    
    context = {
        'chatbot_times': chatbot_times,
        'graphical_times': graphical_times,
        'chatbot_quality': chatbot_quality,
        'graphical_quality': graphical_quality,
        'statistical_results': statistical_results,
    }
    return render(request, 'analytics/comparison.html', context)

@login_required
def generate_report(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title', f'Experiment Report {timezone.now().strftime("%Y-%m-%d")}')
        description = request.POST.get('description', '')
        
        # Gather statistics
        total_participants = User.objects.filter(user_type='participant').count()
        
        chatbot_participants = Submission.objects.filter(
            assignment__task__tool_type='chatbot'
        ).values('assignment__user').distinct().count()
        
        graphical_participants = Submission.objects.filter(
            assignment__task__tool_type='graphical'
        ).values('assignment__user').distinct().count()
        
        # Calculate averages
        chatbot_avg_time = Submission.objects.filter(
            assignment__task__tool_type='chatbot'
        ).aggregate(Avg('assignment__time_taken'))['assignment__time_taken__avg']
        
        graphical_avg_time = Submission.objects.filter(
            assignment__task__tool_type='graphical'
        ).aggregate(Avg('assignment__time_taken'))['assignment__time_taken__avg']
        
        chatbot_avg_quality = Submission.objects.filter(
            assignment__task__tool_type='chatbot'
        ).aggregate(Avg('completeness_score'))['completeness_score__avg']
        
        graphical_avg_quality = Submission.objects.filter(
            assignment__task__tool_type='graphical'
        ).aggregate(Avg('completeness_score'))['completeness_score__avg']
        
        # Statistical analysis (same as tool_comparison)
        chatbot_times = list(Submission.objects.filter(
            assignment__task__tool_type='chatbot',
            assignment__time_taken__isnull=False
        ).values_list('assignment__time_taken', flat=True))
        
        graphical_times = list(Submission.objects.filter(
            assignment__task__tool_type='graphical',
            assignment__time_taken__isnull=False
        ).values_list('assignment__time_taken', flat=True))
        
        statistical_results = {}
        if len(chatbot_times) > 0 and len(graphical_times) > 0:
            t_stat, p_value = stats.ttest_ind(chatbot_times, graphical_times)
            statistical_results['time_comparison'] = {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        # Create report
        report = ExperimentReport.objects.create(
            title=title,
            description=description,
            generated_by=request.user,
            total_participants=total_participants,
            chatbot_participants=chatbot_participants,
            graphical_participants=graphical_participants,
            avg_time_chatbot=chatbot_avg_time,
            avg_time_graphical=graphical_avg_time,
            avg_quality_chatbot=chatbot_avg_quality,
            avg_quality_graphical=graphical_avg_quality,
            statistical_results=statistical_results
        )
        
        messages.success(request, 'Report generated successfully!')
        return redirect('analytics:report_detail', pk=report.pk)
    
    return render(request, 'analytics/generate_report.html')

@login_required
def report_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    reports = ExperimentReport.objects.all().order_by('-generated_at')
    
    context = {'reports': reports}
    return render(request, 'analytics/report_list.html', context)

@login_required
def report_detail(request, pk):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    report = get_object_or_404(ExperimentReport, pk=pk)
    
    context = {'report': report}
    return render(request, 'analytics/report_detail.html', context)
