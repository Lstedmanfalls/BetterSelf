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
    path('quotes/<int:quote_id>/like', views.like), #POST request to create like object
    path('quotes/<int:quote_id>/unlike', views.unlike), #POST request to delete like object
    # #Start Program Page
    path('program', views.new_program), #GET request to display program creation page
    path('program/create_program', views.create_program), #POST request to create program
    # #Specific Program Page
    path('program/<int:program_id>', views.view_program), #GET request to display a specific program's info
    path('program/<int:program_id>/create_baseline', views.create_baseline), #POST request to create baseline entry
    path('program/<int:program_id>/create_intervention', views.create_intervention), #POST request to create intervention entrys
    path('program/<int:program_id>/delete_baseline', views.delete_baseline), #POST request to delete a specific baseline entry
    path('program/<int:program_id>/delete_intervention', views.delete_intervention), #POST request to delete a specific intervention entry
    # # My Account Page
    path('user/<int:user_id>/account', views.account), #GET request to view specific account page
    path('user/<int:user_id>/account/update_password', views.update_password), #POST request to change password
    path('user/<int:user_id>/account/update_display_name', views.update_display_name), #POST request to change password
    path('user/<int:user_id>/account/update_quote', views.update_quote), #POST request to update a specific quote
    path('user/<int:user_id>/account/delete_quote', views.delete_quote), #POST request to delete a specific object
    path('user/<int:user_id>/account/unlike', views.account_unlike), #POST request to delete a like object from quote on account page
]