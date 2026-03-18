from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from tasks.models import TaskAssignment
from .models import DiagramSession, DiagramAction
import json
import uuid

@login_required
def graphical_interface(request, assignment_id):
    assignment = get_object_or_404(
        TaskAssignment, 
        pk=assignment_id, 
        user=request.user,
        task__tool_type='graphical'
    )
    
    # Create or get diagram session
    session, created = DiagramSession.objects.get_or_create(
        assignment=assignment,
        defaults={'session_id': str(uuid.uuid4())}
    )
    
    # Update assignment status
    if assignment.status == 'pending':
        assignment.status = 'in_progress'
        assignment.started_at = timezone.now()
        assignment.save()
    
    context = {
        'assignment': assignment,
        'session': session,
    }
    return render(request, 'graphical_tool/interface.html', context)

@login_required
def save_diagram(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        diagram_data = data.get('diagram_data')
        
        session = get_object_or_404(DiagramSession, session_id=session_id)
        session.diagram_data = diagram_data
        session.save()
        
        return JsonResponse({'status': 'success', 'message': 'Diagram saved successfully'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def log_action(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        action_type = data.get('action_type')
        action_data = data.get('action_data')
        
        session = get_object_or_404(DiagramSession, session_id=session_id)
        
        DiagramAction.objects.create(
            session=session,
            action_type=action_type,
            action_data=action_data
        )
        
        session.action_count += 1
        session.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def load_diagram(request, session_id):
    session = get_object_or_404(DiagramSession, session_id=session_id)
    
    return JsonResponse({
        'diagram_data': session.diagram_data,
        'action_count': session.action_count
    })
