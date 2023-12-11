from django.urls import path
from . import views

urlpatterns = [
    # First page, not logged in
    path('', views.get_landing_page),
    # First page, logged in
    path("home", views.get_home),

    # Motivation Page
    path("quotes", views.get_quotes_wall),
    path('quotes/create_quote', views.create_quote),
    path('quotes/like', views.like_quote), 
    path('quotes/unlike', views.unlike_quote), 
    
    # Program Page
    # Start Program Page
    path('program', views.get_new_program),
    path('program/create_program', views.create_program), #POST request to create program
    # Specific Program Page
    path('program/<int:program_id>', views.get_program), #GET request to display a specific program's info
    path('program/<int:program_id>/create_baseline', views.create_baseline), #POST request to create baseline entry
    path('program/<int:program_id>/create_intervention', views.create_intervention), #POST request to create intervention entrys
    path('program/<int:program_id>/delete_baseline', views.delete_baseline), #POST request to delete a specific baseline entry
    path('program/<int:program_id>/delete_intervention', views.delete_intervention), #POST request to delete a specific intervention entry
    # path('program/<int:program_id>/update_goal', views.update_goal), #POST request to update the goal to a new goal

    # Program Note
    path('baseline_note/<int:baseline_id>', views.view_baseline_note), #GET request to view a specific baseline note
    path('intervention_note/<int:intervention_id>', views.view_intervention_note), #GET request to view a specific baseline note
    
    # Account Page
    path('account', views.account), #GET request to view specific account page
    path('account/delete_program', views.delete_program), #POST request to delete a specific program
    path('account/update_password', views.update_password), #POST request to change password
    path('account/update_display_name', views.update_display_name), #POST request to change password
    path('account/update_quote', views.update_quote), #POST request to update a specific quote
    path('account/delete_quote', views.delete_quote), #POST request to delete a specific quote
    path('account/unlike', views.account_unlike), #POST request to delete a like object from quote on account page
]