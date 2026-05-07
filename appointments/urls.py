from django.urls import path
from . import views

urlpatterns = [
    path('',          views.home,               name='home'),
    path('about/',    views.about,              name='about'),
    path('patients/', views.patients,           name='patients'),
    path('rates/',    views.rates,              name='rates'),
    path('contact/',  views.contact,            name='contact'),
    path('book/',     views.book_appointment,   name='book_appointment'),
    path('book/success/', views.appointment_success, name='appointment_success'),
    path('chatbot/',  views.chatbot_view,       name='chatbot'),
]
