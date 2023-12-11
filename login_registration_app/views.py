from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
import bcrypt

def admin(request):
    context = {
    "all_the_users": User.objects.all(),
    }
    return render(request, "login.html", context)

def register(request):
    if request.method != "POST":
        return redirect("/admin")
    
    errors = User.objects.register_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/admin")
    
    password = request.POST['password']
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User.objects.create(first_name = request.POST["first_name"], last_name = request.POST["last_name"], display_name = request.POST['display_name'], email = request.POST['email'], password=pw_hash)
    request.session['user_id'] = user.id
    return redirect("/home")

def login(request):
    if request.method != "POST":
        return redirect("/admin")
    errors = User.objects.login_validator(request.POST)
    if len(errors) > 0:
        for key, value in errors.items():
            messages.error(request, value)
        return redirect("/admin")
    
    user = User.objects.filter(email=request.POST["email"])
    if user: 
        logged_user = user[0] 
        if bcrypt.checkpw(request.POST['password'].encode(), logged_user.password.encode()):
            request.session["user_id"] = logged_user.id
        return redirect("/home")


def logout(request):
    request.session.flush()
    return redirect("/")