from django.http import request
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from login_registration_app.models import User
from .models import Intervention, Quote, Program, Baseline, Intervention
from django.db.models import Avg, base
from datetime import date
import bcrypt

# --------- Landing page viewable to public
def landing_page(request): #GET REQUEST
    return render(request, "landing_page.html")

# --------- Landing page after login (new links / access to links)
def home(request): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    context = {
    "this_user": User.objects.get(id=request.session["user_id"]),
    }
    return render(request, "home.html", context)

# --------- Quotes wall page
def quotes_wall(request): #GET REQUEST
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    else:
        all_the_quotes = Quote.objects.all().order_by("-created_at")
        context = {
        "this_user": User.objects.get(id=request.session["user_id"]),
        "all_the_quotes": all_the_quotes,
    }
    return render(request, "quotes_wall.html", context)

def create_quote(request): #POST REQUEST
    this_user = User.objects.get(id=request.session["user_id"])
    errors = Quote.objects.create_quote_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/quotes")
    elif request.method != "POST":
        return redirect("/quotes")
    elif request.method == "POST":
        create = Quote.objects.create(quote = request.POST["quote"], author = request.POST["author"], user_who_uploaded = this_user)
        this_quote = Quote.objects.get(id = create.id)
        messages.success(request, "Quote added")
    return redirect("/quotes")

def like(request): #POST REQUEST
    if request.method != "POST":
        return redirect("/quotes")
    if request.method == "POST":
        this_user = User.objects.get(id = request.session["user_id"])
        this_quote = Quote.objects.get(id = request.POST["quote_id"])
        this_user.quote_liker.add(this_quote)
    return render(request, "quotes_wall.html")

def unlike(request): #POST REQUEST
    this_user = User.objects.get(id = request.session["user_id"])
    this_quote = Quote.objects.get(id = request.POST["quote_id"])
    if request.method != "POST":
        return redirect("/quotes")
    if request.method == "POST":
        this_user.quote_liker.remove(this_quote)
    return redirect("/quotes")

# --------- New program page
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

# ---------  Specific program page, for a specific user
def view_program(request, program_id): #GET REQUEST
    # User must be logged in
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    this_user = User.objects.get(id=request.session["user_id"])
    this_program = Program.objects.get(id = program_id)
    
    # User cannot view another person's programs
    if this_user.id != this_program.user_program.id:
        return redirect ("/home")
    
    # Determine direction of desired behavior change
    if this_program.direction == 0:
        change_direction = "decrease"
    else:
        change_direction = "increase"

    # Default context before any baseline entries have been added
    context = {
        "this_user":this_user,
        "this_program": this_program,
        "change_direction": change_direction,
        }

    existing_baseline = this_program.baseline_program.all()
    existing_intervention = this_program.intervention_program.all()

    # If a baseline entry has been added, user can see table with baseline data    
    if len(existing_baseline) > 0:
        baseline = True
        context["baseline"] = baseline
        
        # If at least 3 baseline entries have been added, user can see baseline average and goal
        if len(existing_baseline) >= 3:
            intervention_ready = True

            # Goal is set as 10% more or less than the baseline average, depending on desired change direction
            baseline_avg = int(this_program.baseline_program.aggregate(Avg('total'))["total__avg"])
            baseline_avg_statement = f"{baseline_avg} {this_program.measurement.lower()} each day"
            if this_program.direction == 0:
                goal = int(baseline_avg - (baseline_avg * .1))
                goal_statement = f"No more than {goal} {this_program.measurement.lower()} per day"
            else:
                goal = int(baseline_avg + (baseline_avg * .1))
                goal_statement = f"At least {goal} {this_program.measurement.lower()} per day"
            context["intervention_ready"] = intervention_ready
            context["baseline_avg"] = baseline_avg
            context["baseline_avg_statement"] = baseline_avg_statement
            context["goal"] = goal
            context["goal_statement"] = goal_statement

        # If an intervention entry has been added, user can see intervention data in the table
            if len(existing_intervention) > 0:
                intervention = True
                context["intervention"] = intervention

        # # If at least 7 intervention entries have been added, and goal has been met each time, user can generate a new goal
        # count = 0
        # if len(existing_intervention) >= 7:
        #     for i in existing_intervention:
        #         if change_direction == "decrease":
        #             if i.total <= goal:
        #                 count += 1
        #                 if count >=7:
        #                     new_goal_ready = True
        #                     context["new_goal_ready"] = new_goal_ready
        #         if change_direction == "increase":
        #             if i.total >= goal:
        #                 count += 1
        #                 if count >=7:
        #                     new_goal_ready = True
        #                     context["new_goal_ready"] = new_goal_ready
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

def delete_baseline(request, program_id): #POST REQUEST
    this_baseline = Baseline.objects.get(id = request.POST["baseline_id"])
    if request.method != "POST":
        return redirect(f"/program/{program_id}")
    if request.method == "POST":
        this_baseline.delete()        
    return redirect(f"/program/{program_id}")

def delete_intervention(request, program_id): #POST REQUEST
    this_intervention = Intervention.objects.get(id = request.POST["intervention_id"])
    if request.method != "POST":
        return redirect(f"/program/{program_id}")
    if request.method == "POST":
        this_intervention.delete()        
    return redirect(f"/program/{program_id}")

def view_baseline_note(request, baseline_id): #GET REQUEST
    this_baseline = Baseline.objects.get(id = baseline_id)
    context = {
    "this_baseline":this_baseline
    }
    return render(request, "view_baseline_note.html", context)

def view_intervention_note(request, intervention_id): #GET REQUEST
    this_intervention = Intervention.objects.get(id = intervention_id)
    context = {
    "this_intervention":this_intervention
    }
    return render(request, "view_intervention_note.html", context)

# --------- Specific user account page
def account(request, user_id): #GET REQUEST
        # User must be logged in
    if "user_id" not in request.session:
        messages.error(request, "You must be logged in to view this site")
        return redirect ("/admin")
    this_user = User.objects.get(id = request.session["user_id"])

    # User cannot view another person's account page
    if this_user.id != user_id:
        return redirect ("/home")
        
    programs = this_user.program_user.all()
    context = {
        "this_user": this_user,
        "programs": programs
    }
    return render(request, "account.html", context)

def delete_program(request, user_id): #POST REQUEST
    this_program = Program.objects.get(id = request.POST["program_id"])
    if request.method != "POST":
        return redirect("/home")
    if request.method == "POST":
        this_program.delete()        
    return redirect(f"/user/{user_id}/account")

def update_display_name(request, user_id): #POST REQUEST
    this_user = User.objects.get(id = user_id)
    errors = User.objects.update_display_name_validator(request.POST, request.session)    
    if request.POST['display_name'] == this_user.display_name:
            messages.success(request, "No changes made")
            return redirect(f"/user/{user_id}/account")
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/user/{user_id}/account")
    elif request.method != "POST":
        return redirect("/home")
    elif request.method == "POST":
        this_user = User.objects.get(id = user_id)
        display_name = request.POST['display_name']
        this_user.display_name = display_name
        this_user.save()
        messages.success(request, "Display name updated")
    return redirect(f"/user/{user_id}/account")

def update_password(request, user_id): #POST REQUEST
    errors = User.objects.update_password_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/user/{user_id}/account")
    elif request.method != "POST":
        return redirect("/home")
    elif request.method == "POST":
        this_user = User.objects.get(id = user_id)
        password = request.POST['password']
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        this_user.password = pw_hash
        this_user.save()
        messages.success(request, "Password updated")
    return redirect(f"/user/{user_id}/account")

def update_quote(request, user_id): #POST REQUEST
    this_quote = Quote.objects.get(id = request.POST["quote_id"])
    errors = Quote.objects.update_quote_validator(request.POST)
    if request.POST['quote'] == this_quote.quote and request.POST['author'] == this_quote.author:
            messages.success(request, "No changes made")
            return redirect(f"/user/{user_id}/account")
    elif len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/user/{user_id}/account")
    elif request.method != "POST":
        return redirect("/home")
    elif request.method == "POST":
        this_quote = Quote.objects.get(id = request.POST["quote_id"])
        this_quote.quote = request.POST["quote"]
        this_quote.author = request.POST["author"]
        this_quote.save()
        messages.success(request, "Quote updated")
    return redirect(f"/user/{user_id}/account")

def delete_quote(request, user_id): #POST REQUEST
    this_quote = Quote.objects.get(id = request.POST["quote_id"])
    if request.method != "POST":
        return redirect("/home")
    if request.method == "POST":
        this_quote.delete()        
    return redirect(f"/user/{user_id}/account")

def account_unlike(request, user_id): #POST REQUEST (unlike quote from own account page)
    this_user = User.objects.get(id = request.session["user_id"])
    this_quote = Quote.objects.get(id = request.POST["quote_id"])
    if request.method != "POST":
        return redirect(f"/user/{user_id}/account")
    if request.method == "POST":
        this_user.quote_liker.remove(this_quote)
    return redirect(f"/user/{user_id}/account")