from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from tasks.models import TaskAssignment
from submissions.models import Submission

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            user_type='participant'
        )
        messages.success(request, 'Registration successful! Please login.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')

@login_required
def dashboard_view(request):
    if request.user.is_admin:
        return redirect('adminpanel:dashboard')
    
    assignments = TaskAssignment.objects.filter(user=request.user).select_related('task')
    completed = assignments.filter(status='completed').count()
    pending = assignments.filter(status='pending').count()
    in_progress = assignments.filter(status='in_progress').count()
    
    context = {
        'assignments': assignments[:5],
        'total_tasks': assignments.count(),
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.age = request.POST.get('age')
        user.education_level = request.POST.get('education_level')
        user.uml_experience = request.POST.get('uml_experience')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/profile.html')
