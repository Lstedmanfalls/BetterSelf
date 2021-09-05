from django.http import request
from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from login_registration_app.models import User
from .models import Quote


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
