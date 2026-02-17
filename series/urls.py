from django.urls import path
from . import views

urlpatterns = [
    path('', views.watchlist, name='watchlist'),
    path('add/netflix/', views.add_netflix, name='add_netflix'),
    path('add/prime/', views.add_prime, name='add_prime'),
    path('add/apple/', views.add_apple, name='add_apple'),
    path('add/action/', views.add_action, name='add_action'),
]