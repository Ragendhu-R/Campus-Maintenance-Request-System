from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.http import HttpResponseForbidden

from .models import MaintenanceRequest, RequestComment, UserProfile
from .forms import (
    StudentStaffRegisterForm, 
    CustomLoginForm, 
    MaintenanceRequestForm, 
    StaffRequestUpdateForm, 
    RequestCommentForm
)


def is_staff_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or (hasattr(user, 'profile') and user.profile.is_staff_member))


def home_view(request):
    """
    Landing / Dashboard Home page.
    """
    total_requests = MaintenanceRequest.objects.count()
    completed_requests = MaintenanceRequest.objects.filter(status='COMPLETED').count()
    pending_requests = MaintenanceRequest.objects.filter(status='PENDING').count()
    in_progress_requests = MaintenanceRequest.objects.filter(status='IN_PROGRESS').count()

    recent_requests = []
    if request.user.is_authenticated:
        if is_staff_user(request.user):
            recent_requests = MaintenanceRequest.objects.all()[:5]
        else:
            recent_requests = MaintenanceRequest.objects.filter(user=request.user)[:5]

    context = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'recent_requests': recent_requests,
        'is_staff': is_staff_user(request.user) if request.user.is_authenticated else False,
    }
    return render(request, 'maintenance/home.html', context)


def register_view(request):
    """
    User Registration View.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = StudentStaffRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Campus Maintenance, {user.first_name or user.username}! Your account was created successfully.")
            if is_staff_user(user):
                return redirect('staff_dashboard')
            return redirect('my_requests')
        else:
            messages.error(request, "Please correct the errors below to complete your registration.")
    else:
        form = StudentStaffRegisterForm()

    return render(request, 'maintenance/register.html', {'form': form})


def login_view(request):
    """
    User Login View.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if is_staff_user(user):
                return redirect('staff_dashboard')
            return redirect('my_requests')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomLoginForm()

    return render(request, 'maintenance/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    User Logout View.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def my_requests_view(request):
    """
    Display requests submitted by the logged-in user with filter & search capabilities.
    """
    requests_qs = MaintenanceRequest.objects.filter(user=request.user)

    # Filter & Search parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    priority_filter = request.GET.get('priority', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        requests_qs = requests_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if category_filter:
        requests_qs = requests_qs.filter(category=category_filter)

    if priority_filter:
        requests_qs = requests_qs.filter(priority=priority_filter)

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    # Summary metrics for user's own requests
    all_user_reqs = MaintenanceRequest.objects.filter(user=request.user)
    stats = {
        'total': all_user_reqs.count(),
        'pending': all_user_reqs.filter(status='PENDING').count(),
        'in_progress': all_user_reqs.filter(status='IN_PROGRESS').count(),
        'completed': all_user_reqs.filter(status='COMPLETED').count(),
        'rejected': all_user_reqs.filter(status='REJECTED').count(),
    }

    context = {
        'requests': requests_qs,
        'stats': stats,
        'search_query': search_query,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'category_choices': MaintenanceRequest.CATEGORY_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
    }
    return render(request, 'maintenance/my_requests.html', context)


@login_required
def create_request_view(request):
    """
    Form to allow authenticated users to submit a new maintenance request.
    """
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.user = request.user
            req.status = 'PENDING'
            req.save()
            messages.success(request, f"Maintenance request '#{req.id}: {req.title}' submitted successfully!")
            return redirect('my_requests')
        else:
            messages.error(request, "Please check the form input errors below.")
    else:
        form = MaintenanceRequestForm()

    return render(request, 'maintenance/create_request.html', {'form': form})


@login_required
def request_detail_view(request, pk):
    """
    View details of a specific request, timeline, and comment thread.
    """
    req_obj = get_object_or_404(MaintenanceRequest, pk=pk)

    # Authorization check: user must own request or be staff
    if req_obj.user != request.user and not is_staff_user(request.user):
        messages.error(request, "You are not authorized to view this maintenance request.")
        return redirect('my_requests')

    if request.method == 'POST':
        comment_form = RequestCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.request = req_obj
            comment.user = request.user
            comment.save()
            messages.success(request, "Comment added successfully.")
            return redirect('request_detail', pk=pk)
    else:
        comment_form = RequestCommentForm()

    staff_update_form = StaffRequestUpdateForm(instance=req_obj) if is_staff_user(request.user) else None

    context = {
        'req_obj': req_obj,
        'comment_form': comment_form,
        'staff_update_form': staff_update_form,
        'is_staff': is_staff_user(request.user),
        'comments': req_obj.comments.all(),
    }
    return render(request, 'maintenance/request_detail.html', context)


@login_required
def edit_request_view(request, pk):
    """
    CRUD operation: Edit an existing maintenance request.
    """
    req_obj = get_object_or_404(MaintenanceRequest, pk=pk)

    # Permission check: must be owner or staff
    if req_obj.user != request.user and not is_staff_user(request.user):
        messages.error(request, "You do not have permission to edit this request.")
        return redirect('my_requests')

    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=req_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Request #{req_obj.id} updated successfully.")
            return redirect('request_detail', pk=req_obj.id)
        else:
            messages.error(request, "Failed to update request. Please check form errors.")
    else:
        form = MaintenanceRequestForm(instance=req_obj)

    context = {
        'form': form,
        'req_obj': req_obj,
    }
    return render(request, 'maintenance/edit_request.html', context)


@login_required
def delete_request_view(request, pk):
    """
    CRUD operation: Delete/Cancel a maintenance request.
    """
    req_obj = get_object_or_404(MaintenanceRequest, pk=pk)

    # Permission check: user can delete their own request or staff can delete
    if req_obj.user != request.user and not is_staff_user(request.user):
        messages.error(request, "You are not authorized to delete this request.")
        return redirect('my_requests')

    if request.method == 'POST':
        title = req_obj.title
        req_id = req_obj.id
        req_obj.delete()
        messages.success(request, f"Maintenance request #{req_id} ('{title}') has been deleted.")
        if is_staff_user(request.user):
            return redirect('staff_dashboard')
        return redirect('my_requests')

    return render(request, 'maintenance/confirm_delete.html', {'req_obj': req_obj})


@login_required
def staff_dashboard_view(request):
    """
    Staff / Admin page to view all campus maintenance requests, filter, and update status.
    """
    if not is_staff_user(request.user):
        messages.error(request, "Access restricted to Maintenance Staff and Admin personnel.")
        return redirect('home')

    requests_qs = MaintenanceRequest.objects.all()

    # Filters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    priority_filter = request.GET.get('priority', '').strip()
    status_filter = request.GET.get('status', '').strip()
    assigned_filter = request.GET.get('assigned', '').strip()

    if search_query:
        requests_qs = requests_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query)
        )

    if category_filter:
        requests_qs = requests_qs.filter(category=category_filter)

    if priority_filter:
        requests_qs = requests_qs.filter(priority=priority_filter)

    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    if assigned_filter == 'me':
        requests_qs = requests_qs.filter(assigned_staff=request.user)
    elif assigned_filter == 'unassigned':
        requests_qs = requests_qs.filter(assigned_staff__isnull=True)

    # Metrics
    total_all = MaintenanceRequest.objects.count()
    pending_count = MaintenanceRequest.objects.filter(status='PENDING').count()
    in_progress_count = MaintenanceRequest.objects.filter(status='IN_PROGRESS').count()
    completed_count = MaintenanceRequest.objects.filter(status='COMPLETED').count()
    urgent_count = MaintenanceRequest.objects.filter(priority='URGENT', status__in=['PENDING', 'IN_PROGRESS']).count()

    context = {
        'requests': requests_qs,
        'total_all': total_all,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'urgent_count': urgent_count,
        'search_query': search_query,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'assigned_filter': assigned_filter,
        'category_choices': MaintenanceRequest.CATEGORY_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
    }
    return render(request, 'maintenance/staff_dashboard.html', context)


@login_required
def staff_update_status_view(request, pk):
    """
    Action endpoint for staff/admin to quickly update a request's status, assignment, and notes.
    """
    if not is_staff_user(request.user):
        messages.error(request, "Permission denied.")
        return redirect('home')

    req_obj = get_object_or_404(MaintenanceRequest, pk=pk)

    if request.method == 'POST':
        form = StaffRequestUpdateForm(request.POST, instance=req_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated status for request #{req_obj.id} to '{req_obj.get_status_display()}'.")
        else:
            messages.error(request, "Error updating status. Please check invalid values.")

    return redirect(request.META.get('HTTP_REFERER', 'staff_dashboard'))
