from django.db import models
import re
import bcrypt

class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        existing_display_name = User.objects.filter(display_name = postData["display_name"])
        existing_email = User.objects.filter(email = postData["email"])
        EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
        if len(postData["first_name"]) < 2:
            errors["first_name"] = "First name must be at least 2 characters"
        if len(postData['last_name']) < 2:
            errors["last_name"] = "Last name must be at least 2 characters"
        if len(postData['display_name']) < 1:
            errors["display_name"] = "Dispaly name is required"
        elif len (existing_display_name) > 0:
            errors["duplicate_display_name"] = "That display name is taken, please choose another"
        if not EMAIL_REGEX.match(postData["email"]):           
            errors["email"] = "Please enter a valid email address."
        elif len(existing_email) > 0:
            errors["duplicate_email"] = "That email is already registered, please login"
        if len(postData['password']) < 8:
            errors["password"] = "Password must be at least 8 character"
        elif postData["password"] != postData["password_confirm"]:
            errors["password_confirm"] = "Passwords do not match"
        return errors
    
    def login_validator(self, postData):
        errors = {}
        existing_email = User.objects.filter(email = postData["email"])
        if len(existing_email) < 1:
            errors["not_found"] = "Email not found, please register"
        else:
            user = User.objects.filter(email = postData["email"])[0]
            if not bcrypt.checkpw(postData['password'].encode(), user.password.encode()):
                errors["invalid_password"] = "Password is incorrect"
        return errors
    
    def update_password_validator(self, postData):
        errors = {}
        if len(postData['password']) < 8:
            errors["password"] = "Password must be at least 8 characters"
        elif postData["password"] != postData["password_confirm"]:
            errors["password_confirm"] = "Passwords do not match"
        return errors

    def update_display_name_validator(self, postData, session):
        user = User.objects.get(id = session['user_id'])
        existing_display_name = User.objects.filter(display_name = postData["display_name"])
        errors = {}
        if len(postData['display_name']) < 1:
            errors["display_name"] = "Display name is required"
        elif len(existing_display_name) and existing_display_name[0].id != user.id:
            errors['duplicate_display_name'] = "That display name is already taken"
        return errors

class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    # quote_uploader
    # quote_liker
    # baseline_user
    # intervention_user
    def __repr__(self):
        return f"Object_Name: {self.id}, {self.first_name}, {self.last_name}, {self.email}, {self.password}"