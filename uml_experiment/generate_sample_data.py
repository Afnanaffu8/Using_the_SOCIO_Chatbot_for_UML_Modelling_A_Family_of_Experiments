import os
import django
import random
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uml_experiment.settings')
django.setup()

from accounts.models import User
from tasks.models import Task, TaskAssignment
from submissions.models import Submission, Feedback
from chatbot.models import ChatSession, ChatMessage
from graphical_tool.models import DiagramSession, DiagramAction
import json

def generate_sample_data():
    print("Generating sample data...")
    
    # 1. Create Admin User
    print("\n1. Creating admin user...")
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@umlexperiment.com',
            'user_type': 'admin',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print("   ✓ Admin user created (username: admin, password: admin123)")
    else:
        print("   • Admin user already exists")
    
    # 2. Create Participant Users
    print("\n2. Creating participant users...")
    participants = []
    education_levels = ["Bachelor's", "Master's", "PhD"]
    uml_experiences = ["Beginner", "Intermediate", "Advanced"]
    
    for i in range(1, 21):  # 20 participants
        username = f"participant{i}"
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'user_type': 'participant',
                'participant_id': f'P{str(i).zfill(6)}',
                'age': random.randint(20, 35),
                'education_level': random.choice(education_levels),
                'uml_experience': random.choice(uml_experiences)
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        participants.append(user)
    print(f"   ✓ {len(participants)} participants created")
    
    # 3. Create Tasks
    print("\n3. Creating tasks...")
    tasks_data = [
        {
            'title': 'Library Management System',
            'description': 'Design a class diagram for a library management system',
            'requirements': '''Create a UML class diagram with the following requirements:
- Library class with attributes for name and location
- Book class with attributes for title, author, ISBN
- Member class with attributes for name, memberId, email
- Borrowing relationship between Member and Book
- Contains relationship between Library and Book''',
            'difficulty': 'easy',
            'tool_type': 'chatbot',
            'expected_classes': 3,
            'expected_relationships': 2,
            'time_limit': 20
        },
        {
            'title': 'Library Management System (Graphical)',
            'description': 'Design a class diagram for a library management system',
            'requirements': '''Create a UML class diagram with the following requirements:
- Library class with attributes for name and location
- Book class with attributes for title, author, ISBN
- Member class with attributes for name, memberId, email
- Borrowing relationship between Member and Book
- Contains relationship between Library and Book''',
            'difficulty': 'easy',
            'tool_type': 'graphical',
            'expected_classes': 3,
            'expected_relationships': 2,
            'time_limit': 20
        },
        {
            'title': 'Online Shopping System',
            'description': 'Design a class diagram for an e-commerce platform',
            'requirements': '''Create a UML class diagram with:
- Customer class with login credentials and contact info
- Product class with details and pricing
- ShoppingCart class to manage items
- Order class with order details
- Payment class with payment methods
- Appropriate relationships between all classes''',
            'difficulty': 'medium',
            'tool_type': 'chatbot',
            'expected_classes': 5,
            'expected_relationships': 4,
            'time_limit': 30
        },
        {
            'title': 'Online Shopping System (Graphical)',
            'description': 'Design a class diagram for an e-commerce platform',
            'requirements': '''Create a UML class diagram with:
- Customer class with login credentials and contact info
- Product class with details and pricing
- ShoppingCart class to manage items
- Order class with order details
- Payment class with payment methods
- Appropriate relationships between all classes''',
            'difficulty': 'medium',
            'tool_type': 'graphical',
            'expected_classes': 5,
            'expected_relationships': 4,
            'time_limit': 30
        },
        {
            'title': 'Hospital Management System',
            'description': 'Design a comprehensive hospital management system',
            'requirements': '''Create a complex UML class diagram including:
- Patient class with medical history
- Doctor class with specialization
- Appointment class with scheduling
- Department class with staff management
- Prescription class with medication details
- Invoice class for billing
- Multiple inheritance and aggregation relationships''',
            'difficulty': 'hard',
            'tool_type': 'chatbot',
            'expected_classes': 6,
            'expected_relationships': 7,
            'time_limit': 40
        },
        {
            'title': 'Hospital Management System (Graphical)',
            'description': 'Design a comprehensive hospital management system',
            'requirements': '''Create a complex UML class diagram including:
- Patient class with medical history
- Doctor class with specialization
- Appointment class with scheduling
- Department class with staff management
- Prescription class with medication details
- Invoice class for billing
- Multiple inheritance and aggregation relationships''',
            'difficulty': 'hard',
            'tool_type': 'graphical',
            'expected_classes': 6,
            'expected_relationships': 7,
            'time_limit': 40
        }
    ]
    
    tasks = []
    for task_data in tasks_data:
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            defaults=task_data
        )
        tasks.append(task)
    print(f"   ✓ {len(tasks)} tasks created")
    
    # 4. Create Task Assignments
    print("\n4. Creating task assignments...")
    assignments_created = 0
    for participant in participants:
        # Assign 2 random tasks to each participant
        assigned_tasks = random.sample(tasks, 2)
        for task in assigned_tasks:
            assignment, created = TaskAssignment.objects.get_or_create(
                user=participant,
                task=task,
                defaults={'status': 'pending'}
            )
            if created:
                assignments_created += 1
    print(f"   ✓ {assignments_created} task assignments created")
    
    # 5. Create Sample Submissions with Realistic Data
    print("\n5. Creating sample submissions...")
    submissions_created = 0
    
    # Sample diagram structures
    library_diagram = {
        'classes': [
            {
                'id': 'class_1',
                'name': 'Library',
                'attributes': ['- name: String', '- location: String'],
                'methods': ['+ addBook(book: Book): void', '+ removeBook(bookId: int): void'],
                'x': 50, 'y': 50
            },
            {
                'id': 'class_2',
                'name': 'Book',
                'attributes': ['- title: String', '- author: String', '- ISBN: String'],
                'methods': ['+ getDetails(): String'],
                'x': 300, 'y': 50
            },
            {
                'id': 'class_3',
                'name': 'Member',
                'attributes': ['- name: String', '- memberId: int', '- email: String'],
                'methods': ['+ borrowBook(book: Book): void', '+ returnBook(book: Book): void'],
                'x': 300, 'y': 250
            }
        ],
        'relationships': [
            {'id': 'rel_1', 'from': 'class_1', 'to': 'class_2', 'type': 'composition', 'label': 'contains'},
            {'id': 'rel_2', 'from': 'class_3', 'to': 'class_2', 'type': 'association', 'label': 'borrows'}
        ]
    }
    
    # Complete 50% of assignments with submissions
    completed_assignments = TaskAssignment.objects.filter(status='pending')[:assignments_created // 2]
    
    for assignment in completed_assignments:
        # Update assignment status
        assignment.status = 'completed'
        assignment.started_at = datetime.now() - timedelta(days=random.randint(1, 10))
        assignment.completed_at = assignment.started_at + timedelta(minutes=random.randint(10, 40))
        assignment.time_taken = int((assignment.completed_at - assignment.started_at).total_seconds())
        assignment.save()
        
        # Create submission
        class_count = assignment.task.expected_classes + random.randint(-1, 1)
        relationship_count = assignment.task.expected_relationships + random.randint(-1, 1)
        
        submission = Submission.objects.create(
            assignment=assignment,
            diagram_data=library_diagram,
            class_count=class_count,
            relationship_count=relationship_count,
            attribute_count=random.randint(5, 15),
            method_count=random.randint(3, 10),
            completeness_score=random.uniform(60, 100),
            correctness_score=random.uniform(65, 95),
            quality_score=random.uniform(60, 95)
        )
        
        # Create feedback
        Feedback.objects.create(
            submission=submission,
            ease_of_use=random.randint(3, 5),
            satisfaction=random.randint(3, 5),
            efficiency=random.randint(3, 5),
            would_recommend=random.choice([True, True, True, False]),
            comments=random.choice([
                'Great tool, very intuitive!',
                'Easy to use and efficient.',
                'Could be improved but overall good.',
                'Very helpful for creating diagrams.',
                ''
            ])
        )
        
        submissions_created += 1
    
    print(f"   ✓ {submissions_created} submissions with feedback created")
    
    print("\n" + "="*60)
    print("SAMPLE DATA GENERATION COMPLETE!")
    print("="*60)
    print("\nLogin Credentials:")
    print("-" * 60)
    print("Admin Account:")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nParticipant Accounts (example):")
    print("  Username: participant1 to participant20")
    print("  Password: password123")
    print("\n" + "="*60)

if __name__ == '__main__':
    generate_sample_data()
