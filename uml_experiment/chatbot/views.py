from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from tasks.models import TaskAssignment
from .models import ChatSession, ChatMessage
import google.genai as genai
from django.conf import settings
import json
import uuid

# Create Gemini client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

@login_required
def chatbot_interface(request, assignment_id):
    assignment = get_object_or_404(
        TaskAssignment, 
        pk=assignment_id, 
        user=request.user,
        task__tool_type='chatbot'
    )
    
    # Create or get chat session
    session, created = ChatSession.objects.get_or_create(
        assignment=assignment,
        defaults={'session_id': str(uuid.uuid4())}
    )
    
    # Update assignment status
    if assignment.status == 'pending':
        assignment.status = 'in_progress'
        assignment.started_at = timezone.now()
        assignment.save()
    
    # Get chat history
    messages = session.messages.all().order_by('timestamp')
    
    context = {
        'assignment': assignment,
        'session': session,
        'messages': messages,
    }
    return render(request, 'chatbot/interface.html', context)

@csrf_exempt
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        user_message = data.get('message')
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            sender='user',
            message=user_message,
            diagram_snapshot=session.diagram_data
        )
        
        # Generate bot response
        bot_response = generate_chatbot_response(
            user_message, 
            session.assignment.task,
            session.diagram_data
        )
        
        # Save bot message
        bot_message = ChatMessage.objects.create(
            session=session,
            sender='bot',
            message=bot_response['message']
        )
        
        # Update diagram if provided
        if bot_response.get('diagram_update'):
            current_diagram = session.diagram_data or {"classes": [], "relationships": []}
            new_diagram = bot_response['diagram_update']
            
            # Merge classes
            if 'classes' in new_diagram:
                # Create a dict of existing classes by name for easy lookup
                existing_classes = {cls['name']: cls for cls in current_diagram.get('classes', [])}
                
                # Update or add new classes
                for new_class in new_diagram['classes']:
                    class_name = new_class['name']
                    if class_name in existing_classes:
                        # Update existing class
                        existing_classes[class_name].update(new_class)
                    else:
                        # Add new class
                        current_diagram['classes'].append(new_class)
            
            # Merge relationships
            if 'relationships' in new_diagram:
                current_relationships = current_diagram.get('relationships', [])
                # For simplicity, just append new relationships (avoid duplicates)
                for new_rel in new_diagram['relationships']:
                    # Check if this relationship already exists
                    exists = any(
                        rel.get('from') == new_rel.get('from') and 
                        rel.get('to') == new_rel.get('to') and 
                        rel.get('type') == new_rel.get('type')
                        for rel in current_relationships
                    )
                    if not exists:
                        current_relationships.append(new_rel)
                
                current_diagram['relationships'] = current_relationships
            
            session.diagram_data = current_diagram
            session.save()
        
        # Update message count
        session.message_count += 2
        session.save()
        
        return JsonResponse({
            'status': 'success',
            'bot_message': bot_response['message'],
            'diagram_data': session.diagram_data,
            'timestamp': bot_message.timestamp.isoformat()
        })
    
    return JsonResponse({'status': 'error'}, status=400)

def generate_chatbot_response(user_message, task, current_diagram):
    """Generate response using Gemini API"""
    
    # Create context prompt
    system_prompt = f"""You are an expert UML class diagram assistant. You help users create UML class diagrams through conversation.

Current Task: {task.title}
Task Description: {task.description}
Requirements: {task.requirements}

Current Diagram State: {json.dumps(current_diagram) if current_diagram else 'Empty diagram'}

Instructions:
1. Understand user's intent from their message
2. Guide them to create proper UML class diagrams
3. When the user asks to create or modify the diagram, ALWAYS include a JSON block with diagram updates
4. Provide constructive feedback on their diagram
5. Be concise and helpful

IMPORTANT: When suggesting diagram changes, you MUST format them as a JSON code block like this:

```json
{{
    "classes": [
        {{
            "name": "Book",
            "attributes": ["title: String", "author: String", "isbn: String"],
            "methods": ["getTitle(): String", "setTitle(title: String): void"]
        }}
    ],
    "relationships": [
        {{
            "from": "Member",
            "to": "Book", 
            "type": "association",
            "label": "borrows"
        }}
    ]
}}
```

The JSON should contain ALL classes and relationships that should exist in the diagram after your changes. Include both existing elements and new ones you want to add.

User Message: {user_message}

If the user is asking to create or modify the diagram, include the complete JSON block at the end of your response."""
    
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=system_prompt
        )
        
        response_text = response.text
        
        # Try to extract diagram JSON if present
        diagram_update = None
        
        # Look for JSON code blocks first
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            if json_end > json_start:
                json_str = response_text[json_start:json_end].strip()
                try:
                    diagram_update = json.loads(json_str)
                    # Remove JSON from message
                    response_text = response_text[:json_start-7] + response_text[json_end+3:]
                except json.JSONDecodeError:
                    pass
        
        # If no JSON block found, try to find JSON objects in the text
        if diagram_update is None:
            # Look for patterns like {"classes": ...} or {"relationships": ...}
            import re
            json_pattern = r'\{[^{}]*"classes?"[^{}]*\}|\{[^{}]*"relationships?"[^{}]*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if 'classes' in parsed or 'relationships' in parsed:
                        diagram_update = parsed
                        # Remove the JSON from the message
                        response_text = response_text.replace(match, '').strip()
                        break
                except json.JSONDecodeError:
                    continue
        
        result = {
            'message': response_text.strip(),
            'diagram_update': diagram_update
        }
        return result
        
    except Exception as e:
        return {
            'message': f"I'm having trouble processing that. Could you rephrase? Error: {str(e)}",
            'diagram_update': None
        }

@csrf_exempt
@login_required
def save_diagram(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        session_id = data.get('session_id')
        diagram_data = data.get('diagram_data')
        
        session = get_object_or_404(ChatSession, session_id=session_id)
        session.diagram_data = diagram_data
        session.save()
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_chat_history(request, session_id):
    session = get_object_or_404(ChatSession, session_id=session_id)
    messages = session.messages.all().order_by('timestamp')
    
    message_list = [{
        'sender': msg.sender,
        'message': msg.message,
        'timestamp': msg.timestamp.isoformat()
    } for msg in messages]
    
    return JsonResponse({
        'messages': message_list,
        'diagram_data': session.diagram_data
    })
