from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models.query_utils import Q
from login_registration_app.models import User
from datetime import date

class QuoteManager(models.Manager):
    def create_quote_validator(self, postData):
        existing_quotes = Quote.objects.filter(quote = postData['quote'])
        errors = {}
        if len(postData['quote']) < 10:
            errors['label'] = "Quote should be at least 10 characters"
        if len(postData['author']) < 5:
            errors['author'] = "Author should be at least 5 characters"
        elif len(existing_quotes) > 0:
            errors['duplicate'] = "That quote already exists"
        return errors
    
    def update_quote_validator(self, postData):
        errors = {}
        if len(postData['quote']) < 10:
            errors['label'] = "Quote should be at least 10 characters"
        if len(postData['author']) < 5:
            errors['author'] = "Author should be at least 5 characters"
        return errors

class ProgramManager(models.Manager):
    def create_program_validator(self, postData):
        errors = {}
        if len(postData['behavior']) < 3:
            errors['behavior'] = "Behavior should be at least 3 characters"
        if len(postData['measurement']) < 2:
            errors['measurement'] = "Unit of measurement should be at least 2 characters"
        if len(postData['reason']) < 10:
            errors['reason'] = "Reason should be at least 10 characters"
        return errors

class BaselineManager(models.Manager):
    def create_baseline_validator(self, postData):
        today = date.today()
        errors = {}
        if str(today) < postData['date']:
            errors['future_date'] = "Date cannot be in the future"
        elif postData['date'] <= "2021-09-01":
            errors['invalid_date'] = "Date is not valid"
        if len(postData['total']) == 0:
            errors['total'] = "You must enter a total"
        if len(postData['notes']) > 0 and len(postData['notes']) < 5 :
            errors['notes'] = "Notes can be blank or at least 5 characters"
        return errors

class InterventionManager(models.Manager):
    def create_intervention_validator(self, postData):
        today = date.today()
        errors = {}
        if str(today) < postData['date']:
            errors['future_date'] = "Date cannot be in the future"
        elif postData['date'] <= "2021-09-01":
            errors['invalid_date'] = "Date is not valid"
        if len(postData['total']) == 0:
            errors['total'] = "You must enter a total"
        if len(postData['notes']) > 0 and len(postData['notes']) < 5 :
            errors['notes'] = "Notes can be blank or at least 5 characters"
        return errors

class Quote(models.Model):
    id = models.BigAutoField(primary_key=True)
    quote = models.TextField()    
    author = models.CharField(max_length=255)
    user_who_uploaded = models.ForeignKey(User, related_name= "quote_uploader", on_delete = models.CASCADE)
    user_who_liked = models.ManyToManyField(User, related_name = "quote_liker")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuoteManager()

class Program(models.Model):
    id = models.BigAutoField(primary_key=True)
    behavior = models.CharField(max_length=255)
    measurement = models.CharField(max_length=255)
    direction = models.IntegerField()
    reason = models.TextField()
    user_program = models.ForeignKey(User, related_name="program_user", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    goal = models.IntegerField(null = True)
    objects = ProgramManager()
    # baseline_program
    # intervention_program

class Baseline(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateField()
    total = models.IntegerField()
    notes = models.TextField()
    user_baseline = models.ForeignKey(User, related_name="baseline_user", on_delete = models.CASCADE)
    program_baseline = models.ForeignKey(Program, related_name="baseline_program", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = BaselineManager()

class Intervention(models.Model):
    id = models.BigAutoField(primary_key=True)
    date = models.DateField()
    total = models.IntegerField()
    notes = models.TextField()
    user_intervention = models.ForeignKey(User, related_name="intervention_user", on_delete = models.CASCADE)
    program_intervention = models.ForeignKey(Program, related_name="intervention_program", on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = InterventionManager()