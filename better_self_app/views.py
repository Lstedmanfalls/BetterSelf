from django.http import request
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from login_registration_app.models import User
from .models import Intervention, Quote, Program, Baseline, Intervention
from django.db.models import Avg, base
from datetime import date

def landing_page(request): #GET REQUEST
    return render(request, "landing_page.html")

def home(request): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    context = {
    "this_user": User.objects.get(id=request.session["user_id"]),
    }
    return render(request, "home.html", context)
    
def quotes_wall(request): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    else:
        context = {
        "this_user": User.objects.get(id=request.session["user_id"]),
        "all_the_quotes": Quote.objects.all(),
    }
    return render(request, "quotes_wall.html", context)

def create_quote(request): #POST REQUEST
    this_user = User.objects.get(id=request.session["user_id"])
    errors = Quote.objects.create_quote_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/qoutes")
    elif request.method != "POST":
        return redirect("/quotes")
    elif request.method == "POST":
        create = Quote.objects.create(quote = request.POST["quote"], author = request.POST["author"], user_who_uploaded = this_user)
        this_quote = Quote.objects.get(id = create.id)
        this_quote.user_who_liked.add(this_user)        
        messages.success(request, "Quote added")
    return redirect("/quotes")

def like(request, quote_id): #POST REQUEST
    this_user = User.objects.get(id = request.session["user_id"])
    this_quote = Quote.objects.get(id = quote_id)
    if request.method != "POST":
        return redirect("/quotes")
    if request.method == "POST":
        this_user.quote_liker.add(this_quote)
        return redirect("/quotes")

def unlike(request, quote_id): #POST REQUEST
    this_user = User.objects.get(id = request.session["user_id"])
    this_quote = Quote.objects.get(id = quote_id)
    if request.method != "POST":
        return redirect("/quotes")
    if request.method == "POST":
        this_user.quote_liker.remove(this_quote)
    return redirect("/quotes")

def new_program(request): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    else:
        context = {
        "this_user": User.objects.get(id=request.session["user_id"]),
    }
    return render(request, "new_program.html", context)

def create_program(request): #POST REQUEST
    this_user = User.objects.get(id=request.session["user_id"])
    errors = Program.objects.create_program_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/program")
    elif request.method != "POST":
        return redirect("/program")
    elif request.method == "POST":
        create = Program.objects.create(behavior = request.POST["behavior"], measurement = request.POST["measurement"], direction = request.POST["direction"], reason = request.POST["reason"], user_program = this_user)
        program_id = create.id
    return redirect(f"/program/{program_id}")

def view_program(request, program_id): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    this_user = User.objects.get(id=request.session["user_id"])
    this_program = Program.objects.get(id = program_id)
    if this_user.id != this_program.user_program.id:
        return redirect ("/home")
    existing_baseline = this_program.baseline_program.all()
    if len(existing_baseline) > 0:
        baseline = True
        baseline_avg = int(this_program.baseline_program.aggregate(Avg('total'))["total__avg"])
        baseline_avg_statement = f"{baseline_avg} {this_program.measurement.lower()} each day"
        if this_program.direction == 0:
            goal = int(baseline_avg - (baseline_avg * .1))
            change_direction = "decrease"
            goal_statement = f"No more than {goal} {this_program.measurement.lower()} per day"
        else:
            goal = int(baseline_avg + (baseline_avg * .1))
            change_direction = "increase"
            goal_statement = f"At least {goal} {this_program.measurement.lower()} per day" 
        context = {
            "baseline": baseline,
            "baseline_avg": baseline_avg,
            "baseline_avg_statement": baseline_avg_statement,
            "goal": goal,
            "this_program": this_program,
            "change_direction": change_direction,
            "goal_statement" : goal_statement,
        }
        if len(existing_baseline) >= 3:
            intervention_ready = True
            context = {
            "intervention_ready": intervention_ready,
            "baseline": baseline,
            "baseline_avg": baseline_avg,
            "baseline_avg_statement": baseline_avg_statement,
            "goal": goal,
            "this_program": this_program,
            "change_direction": change_direction,
            "goal_statement" : goal_statement,
        }
        existing_intervention = this_program.intervention_program.all()
        if len(existing_intervention) > 0:
            intervention = True
            context = {
            "intervention": intervention,
            "baseline": baseline,
            "baseline_avg": baseline_avg,
            "baseline_avg_statement": baseline_avg_statement,
            "goal": goal,
            "this_program": this_program,
            "change_direction": change_direction,
            "goal_statement" : goal_statement,
        }
    else:
        if this_program.direction == 0:
            change_direction = "decrease"
        else:
            change_direction = "increase"
        context = {
        "this_program": this_program,
        "change_direction": change_direction,
        }
    return render(request, "view_program.html", context)

def create_baseline(request, program_id): #POST REQUEST
    # Need to add validation in here to not let them do another entry for the same day
    this_user = User.objects.get(id=request.session["user_id"])
    this_program = Program.objects.get(id = program_id)
    errors = Baseline.objects.create_baseline_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/program/{program_id}")
    elif request.method != "POST":
        return redirect(f"/program/{program_id}")
    elif request.method == "POST":
        Baseline.objects.create(date = request.POST["date"], total = request.POST["total"], notes = request.POST["notes"], user_baseline = this_user, program_baseline = this_program)
    return redirect(f"/program/{program_id}")
    
def create_intervention(request, program_id): #POST REQUEST
    # Need to add validation in here to not let them do another entry for the same day
    this_user = User.objects.get(id=request.session["user_id"])
    this_program = Program.objects.get(id = program_id)
    errors = Intervention.objects.create_intervention_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/program/{program_id}")
    elif request.method != "POST":
        return redirect(f"/program/{program_id}")
    elif request.method == "POST":
        Intervention.objects.create(date = request.POST["date"], total = request.POST["total"], notes = request.POST["notes"], user_intervention = this_user, program_intervention = this_program)
    return redirect(f"/program/{program_id}")