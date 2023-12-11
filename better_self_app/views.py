from django.shortcuts import render, redirect
from django.contrib import messages
from login_registration_app.models import User
from .models import Intervention, Quote, Program, Baseline, Intervention
from django.db.models import Avg
import bcrypt

# --------- Public landing page
def get_landing_page(request):
    return render(request, "landing_page.html")

# --------- Logged in landing page
def get_home(request):
    if "user_id" not in request.session:
        return redirect ("/admin")  
    
    context = {
    "user": User.objects.get(id=request.session["user_id"]),
    }
    return render(request, "home.html", context)

# --------- Quotes wall page
def get_quotes_wall(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    
    quotes = Quote.objects.order_by("-created_at")
    context = {
    "user": User.objects.get(id=request.session["user_id"]),
    "quotes": quotes,
    }
    return render(request, "quotes_wall.html", context)

def create_quote(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/quotes")
    
    errors = Quote.objects.create_quote_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/quotes")

    user = User.objects.get(id=request.session["user_id"])
    Quote.objects.create(quote = request.POST["quote"], author = request.POST["author"], user_who_uploaded = user)
    messages.success(request, "Quote added")
    return redirect("/quotes")

def like_quote(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/quotes")
    
    user = User.objects.get(id = request.session["user_id"])
    quote = Quote.objects.get(id = request.POST["quote_id"])
    user.quote_liker.add(quote)
    quotes = Quote.objects.all().order_by("-created_at")
    context = {
        "user": User.objects.get(id=request.session["user_id"]),
        "quotes": quotes,
    }
    return render(request, "like_form_snippet.html", context)

def unlike_quote(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/quotes")
    
    user = User.objects.get(id = request.session["user_id"])
    quote = Quote.objects.get(id = request.POST["quote_id"])
    user.quote_liker.remove(quote)
    quotes = Quote.objects.all().order_by("-created_at")
    context = {
        "user": User.objects.get(id=request.session["user_id"]),
        "quotes": quotes,
    }
    return render(request, "like_form_snippet.html", context)

# --------- New program page
def get_new_program(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    
    context = {
    "user": User.objects.get(id=request.session["user_id"]),
    }
    return render(request, "new_program.html", context)

def create_program(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/program")
    errors = Program.objects.create_program_validator(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/program")
    
    user = User.objects.get(id=request.session["user_id"])
    create = Program.objects.create(behavior = request.POST["behavior"], measurement = request.POST["measurement"], direction = request.POST["direction"], reason = request.POST["reason"], user_program = user)
    program_id = create.id
    return redirect(f"/program/{program_id}")

# ---------  Individual program page

def __get_program_goal_context(program, context):
    # Goal is set as baseline average +/- 10%, depending on change direction
    baseline_avg = int(program.baseline_program.aggregate(Avg('total'))["total__avg"])
    context["baseline_avg"] = baseline_avg

    goal_percentage_change = 0.10
    raw_goal_change = baseline_avg * goal_percentage_change
    whole_num_goal_change = raw_goal_change if raw_goal_change >= 1 else 1
    program.goal = baseline_avg - whole_num_goal_change if program.direction == 0 else baseline_avg + whole_num_goal_change
    program.save()
    context["goal"] = program.goal

    goal_statement_start = f"No more than" if program.direction == 0 else f"At least"
    context["goal_statement"] = f"{goal_statement_start} {program.goal} {program.measurement.lower()} per day"
    context["baseline_avg_statement"] = f"{baseline_avg} {program.measurement.lower()} each day"
    return context

def __check_if_ready_for_new_goal(intervention_data, context):
    intervention_last_5 = intervention_data.order_by("-created_at")[:5]
    intervention_avg_last_5 = int(intervention_last_5.aggregate(Avg('total'))["total__avg"])

    ready_for_new_goal = True if (context["change_direction"] == 'increase' and intervention_avg_last_5 >= context["goal"]) or (context["change_direction"] == 'decrease' and intervention_avg_last_5 <= context["goal"]) else False
    return ready_for_new_goal

def __get_program_context(user, program):
    change_direction = "decrease" if program.direction == 0 else "increase"
    context = {
        "user": user,
        "program": program,
        "change_direction": change_direction,
        }
    
    baseline_data = program.baseline_program.all()
    if not baseline_data:
        return context
    
    context["baseline"] = True
    if len(baseline_data) < 3:
        return context
    
    context["intervention_ready"] = True
    context = __get_program_goal_context(program, context) 
    intervention_data = program.intervention_program.all()
    if not intervention_data:
        return context
    
    context["intervention"] = True
    if len(intervention_data) < 5:
        return context
    
    ready_for_new_goal = __check_if_ready_for_new_goal(intervention_data, context)
    if not ready_for_new_goal:
        return context
    
    context["ready_for_new_goal"] = True
    # TODO: Add functionality to increase the goal to 10% +/- the previous goal

    return context

def get_program(request, program_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    user = User.objects.get(id=request.session["user_id"])
    program = Program.objects.get(id = program_id)
    if user.id != program.user_program.id:
        return redirect ("/home")

    context = __get_program_context(user, program)
    return render(request, "view_program.html", context)

def create_baseline(request, program_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect(f"/program/{program_id}")
    
    program = Program.objects.get(id = program_id)
    errors = Baseline.objects.create_baseline_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/program/{program_id}")

    user = User.objects.get(id=request.session["user_id"])
    Baseline.objects.create(date = request.POST["date"], total = request.POST["total"], notes = request.POST["notes"], user_baseline = user, program_baseline = program)
    return redirect(f"/program/{program_id}")
    
def create_intervention(request, program_id):
    if "user_id" not in request.session:
        return redirect ("/admin")

    program = Program.objects.get(id = program_id)
    errors = Intervention.objects.create_intervention_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect(f"/program/{program_id}")
    if request.method != "POST":
        return redirect(f"/program/{program_id}")

    user = User.objects.get(id=request.session["user_id"])
    Intervention.objects.create(date = request.POST["date"], total = request.POST["total"], notes = request.POST["notes"], user_intervention = user, program_intervention = program)
    return redirect(f"/program/{program_id}")

def delete_baseline(request, program_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect(f"/program/{program_id}")
    
    baseline = Baseline.objects.get(id = request.POST["baseline_id"])
    baseline.delete()        
    return redirect(f"/program/{program_id}")

def delete_intervention(request, program_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect(f"/program/{program_id}")
    
    intervention = Intervention.objects.get(id = request.POST["intervention_id"])
    intervention.delete()        
    return redirect(f"/program/{program_id}")

def view_baseline_note(request, baseline_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    
    baseline = Baseline.objects.get(id = baseline_id)
    context = {
    "baseline": baseline
    }
    return render(request, "view_baseline_note.html", context)

def view_intervention_note(request, intervention_id):
    if "user_id" not in request.session:
        return redirect ("/admin")
    
    intervention = Intervention.objects.get(id = intervention_id)
    context = {
    "intervention":intervention
    }
    return render(request, "view_intervention_note.html", context)

# --------- User account page
def account(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    
    user = User.objects.get(id = request.session["user_id"])
    programs = user.program_user.all()
    context = {
        "user": user,
        "programs": programs,
    }
    return render(request, "account.html", context)

def delete_program(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/home")
    
    program = Program.objects.get(id = request.POST["program_id"])
    program.delete()        
    return redirect("/account")

def update_display_name(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/home")
    
    errors = User.objects.update_display_name_validator(request.POST, request.session)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/account")

    user = User.objects.get(id = request.session["user_id"])    
    if request.POST['display_name'] == user.display_name:
        messages.success(request, "No changes made")
        return redirect("/account")
    display_name = request.POST['display_name']
    user.display_name = display_name
    user.save()
    messages.success(request, "Display name updated")
    return redirect("/account")

def update_password(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/home")
    
    errors = User.objects.update_password_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/account")

    user = User.objects.get(id = request.session["user_id"])
    password = request.POST['password']
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user.password = pw_hash
    user.save()
    messages.success(request, "Password updated")
    return redirect("/account")

def update_quote(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/home")
    
    errors = Quote.objects.update_quote_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/account")

    quote = Quote.objects.get(id = request.POST["quote_id"])
    if request.POST['quote'] == quote.quote and request.POST['author'] == quote.author:
        messages.success(request, "No changes made")
        return redirect("/account")    
    quote.quote = request.POST["quote"]
    quote.author = request.POST["author"]
    quote.save()
    messages.success(request, "Quote updated")
    return redirect("/account")

def delete_quote(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/home")

    quote = Quote.objects.get(id = request.POST["quote_id"])
    quote.delete()        
    return redirect("/account")

def account_unlike(request):
    if "user_id" not in request.session:
        return redirect ("/admin")
    if request.method != "POST":
        return redirect("/account")
    
    user = User.objects.get(id = request.session["user_id"])
    quote = Quote.objects.get(id = request.POST["quote_id"])
    programs = user.program_user.all()
    user.quote_liker.remove(quote)
    context = {
        "user": user,
        "programs": programs,
    }
    return render(request, "unlike_form_account_snippet.html", context)