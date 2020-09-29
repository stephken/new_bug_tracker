from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth import login, logout, authenticate
from bug_tracker_app.forms import LoginForm, AddTicketForm, InProgressForm
from bug_tracker_app.models import My_User, Ticket
from django.contrib.auth.decorators import login_required
from bug_tracker.settings import AUTH_USER_MODEL
# Create your views here.
##Chris Warren assisted with this code

@login_required
def index_view(request):
    tickets = Ticket.objects.all()
    return render(request, "index.html", {"title": "Bugtracker", "welcome": "Welcome to Kens What's up, Doc? (Bugs, Bugs, Bugs!!) assessment", "tickets": tickets})


@login_required
def add_ticket(request):
    if request.method == "POST":
        form = AddTicketForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            Ticket.objects.create(
                title=data.get("title"),
                assigned_by=request.user,
                description=data.get("description")
            )
            return HttpResponseRedirect(reverse("home"))
    form = AddTicketForm()
    return render(request, "generic_form.html", {"form": form})

@login_required
def user_detail_view(request, user_id):
    the_user =My_User.objects.filter(id=user_id).first()
    tickets_assigned = Ticket.objects.filter(assigned_to=the_user.id)
    tickets_by = Ticket.objects.filter(assigned_by=the_user.id)
    tickets_completed = Ticket.objects.filter(completed_by=the_user.id)

    return render(request, "user_detail.html", {"user": the_user, "tickets_by": tickets_by, "tickets_assigned": tickets_assigned, "tickets_completed": tickets_completed})

@login_required
def edit_ticket(request, ticket_id):
    edit_ticket = Ticket.objects.get(id=ticket_id)
    if request.method == "POST":
        form = AddTicketForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            edit_ticket.description = data["description"]
            edit_ticket.title = data["title"]
            edit_ticket.save()
        return HttpResponseRedirect(reverse("ticket", args=[edit_ticket.id]))
    data = {
        "description": edit_ticket.description,
        "title": edit_ticket.title,
    }
    form = AddTicketForm(initial=data)
    return render(request, "generic_form.html", {"form": form})

@login_required
def completed_view(request, ticket_id):
    completed = Ticket.objects.get(id=ticket_id)
    completed.ticket_status_choices = 'D'
    completed.completed_by = completed.assigned_to
    completed.assigned_to = None
    completed.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))    

@login_required
def in_progress_view(request, ticket_id):
    in_progress = Ticket.objects.get(id=ticket_id)
    in_progress.ticket_status_choices = "IP"
    in_progress.completed_by = None
    if request.method == "POST":
        form = InProgressForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            in_progress.assigned_to = data["assigned_to"]
            in_progress.save()
        return HttpResponseRedirect(reverse("ticket", args=[in_progress.id]))
    data = {
        "assigned_to": in_progress.assigned_to
    }
    form = InProgressForm(initial=data)
    return render(request, 'generic_form.html', {'form': form})

@login_required
def ticket_detail_view(request, ticket_id):
    the_ticket = Ticket.objects.filter(id=ticket_id).first()
    return render(request, "ticket_detail.html", {"ticket": the_ticket})

@login_required
def invalid_view(request, ticket_id):
    invalid = Ticket.objects.get(id=ticket_id)
    invalid.ticket_status_choices = 'IV'
    invalid.completed_by = None
    invalid.assigned_to = None
    invalid.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        # breakpoint()
        if form.is_valid():
            data=form.cleaned_data
            user=authenticate(
                request, username=data.get("username"), password=data.get("password")
            )
            if user:
                login(request, user)
                return HttpResponseRedirect(reverse("home"))

    form = LoginForm()
    return render(request, "generic_form.html", {"form": form})


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("home"))