from django.http import request
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from login_registration_app.models import User
from .models import Quote, Program, Baseline
from django.db.models import Avg, base
from datetime import date

def landing_page(request): #GET REQUEST
    return render(request, "landing_page.html")

def home(request): #GET REQUEST
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
    this_program = Program.objects.get(id = program_id)
    baseline_avg = int(this_program.baseline_program.aggregate(Avg('total'))["total__avg"])
    if this_program.direction == 0:
        change_direction = "decrease"
        goal_statement = "No more than"
        goal = int(baseline_avg - (baseline_avg * .1))
    else:
        change_direction = "increase"
        goal_statement = "At least"
        goal = int(baseline_avg + (baseline_avg * .1))
    context = {
    "this_program": this_program,
    "change_direction": change_direction,
    "goal_statement" : goal_statement,
    "baseline_avg": baseline_avg,
    "goal": goal
    }
    return render(request, "view_program.html", context)

def create_baseline(request, program_id): #POST REQUEST
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
