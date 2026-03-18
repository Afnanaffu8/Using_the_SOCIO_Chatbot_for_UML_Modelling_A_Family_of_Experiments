from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from tasks.models import TaskAssignment
from chatbot.models import ChatSession
from graphical_tool.models import DiagramSession
from .models import Submission, Feedback
import json

@login_required
def submit_diagram(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, pk=assignment_id, user=request.user)
    
    if assignment.status == 'completed':
        messages.warning(request, 'This task has already been submitted.')
        return redirect('submissions:my_submissions')
    
    # Get diagram data based on tool type
    if assignment.task.tool_type == 'chatbot':
        try:
            session = ChatSession.objects.get(assignment=assignment)
            diagram_data = session.diagram_data
        except ChatSession.DoesNotExist:
            messages.error(request, 'No chat session found.')
            return redirect('tasks:my_tasks')
    else:  # graphical
        try:
            session = DiagramSession.objects.get(assignment=assignment)
            diagram_data = session.diagram_data
        except DiagramSession.DoesNotExist:
            messages.error(request, 'No diagram session found.')
            return redirect('tasks:my_tasks')
    
    if request.method == 'POST':
        # Calculate time taken
        if assignment.started_at:
            time_taken = (timezone.now() - assignment.started_at).total_seconds()
        else:
            time_taken = 0
        
        # Count elements
        class_count = len(diagram_data.get('classes', []))
        relationship_count = len(diagram_data.get('relationships', []))
        
        attribute_count = 0
        method_count = 0
        for cls in diagram_data.get('classes', []):
            attribute_count += len(cls.get('attributes', []))
            method_count += len(cls.get('methods', []))
        
        # Calculate basic quality scores
        completeness_score = calculate_completeness_score(
            class_count, 
            relationship_count,
            assignment.task.expected_classes,
            assignment.task.expected_relationships
        )
        
        # Create submission
        submission = Submission.objects.create(
            assignment=assignment,
            diagram_data=diagram_data,
            class_count=class_count,
            relationship_count=relationship_count,
            attribute_count=attribute_count,
            method_count=method_count,
            completeness_score=completeness_score
        )
        
        # Update assignment
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.time_taken = int(time_taken)
        assignment.save()
        
        messages.success(request, 'Diagram submitted successfully!')
        return redirect('submissions:feedback', submission_id=submission.id)
    
    context = {
        'assignment': assignment,
        'diagram_data': diagram_data,
    }
    return render(request, 'submissions/submit.html', context)

def calculate_completeness_score(class_count, rel_count, expected_classes, expected_rels):
    """Calculate completeness score based on expected vs actual counts"""
    if expected_classes == 0 and expected_rels == 0:
        return 100.0
    
    class_score = min((class_count / expected_classes) * 100, 100) if expected_classes > 0 else 100
    rel_score = min((rel_count / expected_rels) * 100, 100) if expected_rels > 0 else 100
    
    return (class_score + rel_score) / 2

@login_required
def submit_feedback(request, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id, assignment__user=request.user)
    
    if hasattr(submission, 'feedback'):
        messages.info(request, 'You have already submitted feedback for this task.')
        return redirect('submissions:my_submissions')
    
    if request.method == 'POST':
        Feedback.objects.create(
            submission=submission,
            ease_of_use=request.POST.get('ease_of_use'),
            satisfaction=request.POST.get('satisfaction'),
            efficiency=request.POST.get('efficiency'),
            would_recommend=request.POST.get('would_recommend') == 'yes',
            comments=request.POST.get('comments', '')
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('submissions:my_submissions')
    
    context = {'submission': submission}
    return render(request, 'submissions/feedback.html', context)

@login_required
def my_submissions(request):
    submissions = Submission.objects.filter(
        assignment__user=request.user
    ).select_related('assignment__task').order_by('-submitted_at')
    
    context = {'submissions': submissions}
    return render(request, 'submissions/my_submissions.html', context)

@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(
        Submission, 
        pk=pk,
        assignment__user=request.user
    )
    
    context = {'submission': submission}
    return render(request, 'submissions/detail.html', context)
