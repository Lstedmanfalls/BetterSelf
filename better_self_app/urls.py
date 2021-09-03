from django.urls import path
from . import views

urlpatterns = [
    #First page, not logged in
    path('', views.landing_page), #GET request to display landing page
    #First page, logged in
    path("home", views.home), #GET request to display home page
    # Motivational Quotes Page
    path("quotes", views.quotes_wall), #GET request to display quotes wall
    path('quotes/create_quote', views.create_quote), #POST request to create quote object
    # path('quotes/like', views.like), #POST request to create like object
    # path('quotes/unlike', views.unlike), #POST request to delete like object
    # #Start Program Page
    # path('program', views.add_program), #GET request to display program creation page
    # path('program/create_program', views.create_program), #POST request to create program
    # #Specific Program Page
    # path('program/<int:program_id>', views.view_program), #GET request to display a specific program's info
    # path('program/<int:program_id>/add_baseline', views.add_baseline), #POST request to create baseline entry
    # path('program/<int:program_id>/add_intervention', views.add_intervention), #POST request to create intervention entry
    # path('program/<int:baseline_id>/edit_baseline', views.edit_baseline), #GET request to display form to edit a specific baseline entry
    # path('program/<int:baseline_id>/update_baseline', views.update_baseline), #POST request to update a specific baseline entry
    # path('program/<int:baseline_id>/delete_baseline', views.delete_baseline), #POST request to delete a specific baseline entry
    # path('program/<int:intervention_id>/edit_intervention', views.edit_intervention), #GET request to display form to edit specific intervention entry
    # path('program/<int:intervention_id>/update_intervention', views.update_intervention), #POST request to update a specific intervention entry
    # path('program/<int:intervention_id>/delete_intervention', views.delete_intervention), #POST request to delete a specific intervention entry
    # # My Account Page
    # path('account/<int:user_id>', views.update_quote), #GET request to view specific account page
    # path('account/<int:quote_id>/edit_quote', views.edit_quote), #GET request to display form to edit a specific quote    
    # path('account/<int:quote_id>/update_quote', views.update_quote), #POST request to update a specific quote
    # path('account/<int:quote_id>/delete_quote', views.delete_quote), #POST request to delete a specific object
    # path('account/<int:quote_id>/unlike', views.account_unlike), #POST request to delete a like object from quote on account page
]