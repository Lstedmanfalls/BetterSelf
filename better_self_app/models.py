from django.db import models
from login_registration_app.models import User

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

    # def update_validator(self, postData):
    #     today = date.today()
    #     existing_objects = Class_Name.objects.filter(label = postData['label'])
    #     errors = {}
    #     if len(postData['label']) < 2:
    #         errors['label'] = "Label should be at least 2 characters"
    #     if str(today) <= postData['label']:
    #         errors['label'] = "Label cannot be now or in the future"
    #     elif len(existing_objects) > 0:
    #         errors['duplicate'] = "That object already exists"
    #     return errors

class Quote(models.Model):
    quote = models.TextField()    
    author = models.CharField(max_length=255)
    user_who_uploaded = models.ForeignKey(User, related_name= "quote_uploader", on_delete = models.CASCADE)
    user_who_liked = models.ManyToManyField(User, related_name = "quote_liker")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuoteManager()
    def __repr__(self):
        quote_uploader = ""
        for i in self.user_who_uploaded():
            quote_uploader += i.first_name + ","
        return f"Quotes: id = {self.id}, quote = {self.quote}, author = {self.author}, uploaded by = {quote_uploader}"