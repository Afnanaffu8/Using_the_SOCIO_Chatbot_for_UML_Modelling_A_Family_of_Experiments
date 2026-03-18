import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(r'd:\projects\Using the SOCIO Chatbot for UML\uml_experiment')

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uml_experiment.settings')
django.setup()

from chatbot.views import generate_chatbot_response
from tasks.models import Task

# Get a task for testing
try:
    task = Task.objects.filter(tool_type='chatbot').first()
    if not task:
        print("No chatbot task found. Creating a test task...")
        task = Task.objects.create(
            title="Test Library System",
            description="Create a UML class diagram for a library system",
            requirements="Include Book and Member classes with appropriate relationships",
            tool_type='chatbot',
            expected_classes=2,
            expected_relationships=1
        )
    
    # Test the chatbot response
    current_diagram = {"classes": [], "relationships": []}
    user_message = "Create a class diagram for a simple library system with Book and Member classes"
    
    print("Testing chatbot response generation...")
    result = generate_chatbot_response(user_message, task, current_diagram)
    
    print("Bot message:", result['message'])
    print("Diagram update:", result['diagram_update'])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()