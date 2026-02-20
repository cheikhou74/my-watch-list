from django.conf import settings
TMDB_API_KEY = settings.TMDB_API_KEY

from django.shortcuts import render, redirect
from .models import Series

import ssl
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import requests
requests.packages.urllib3.disable_warnings()
from django.conf import settings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from django.contrib.auth.decorators import login_required


@login_required
def list(request):
    series_list = Series.objects.filter(user=request.user).order_by('-created_at')  
    return render(request, 'watchlist.html', {'series_list': series_list})
    

TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def watchlist(request):
    """Affiche toutes les séries de la watchlist"""
    series_list = Series.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'watchlist.html', {'series_list': series_list})

def fetch_and_save_series(provider_name, provider_id, genre_id=None, request=None):
    """
    Fonction utilitaire pour appeler l'API TMDB et sauvegarder les séries.
    - provider_name : chaîne ('netflix', 'prime', 'apple', 'action')
    - provider_id : entier TMDB du fournisseur (8,9,2) ou None pour le genre
    - genre_id : entier TMDB du genre (10759 pour Action) ou None
    - request : objet request Django pour gérer la pagination via session
    """
    # Gestion de la page via session (pour obtenir des séries différentes à chaque clic)
    page_key = f'{provider_name}_page'
    page = request.session.get(page_key, 1) if request else 1

    params = {
        'api_key': TMDB_API_KEY,
        'watch_region': 'US',          # Vous pouvez changer si nécessaire
        'sort_by': 'vote_average.desc',
        'page': page
    }
    if provider_id:
        params['with_watch_providers'] = provider_id
    if genre_id:
        params['with_genres'] = genre_id
        # Si on a un genre, on ne veut pas de restriction de fournisseur
        params.pop('with_watch_providers', None)

    response = requests.get(f'{TMDB_BASE_URL}/discover/tv', params=params, verify=False)
    if response.status_code != 200:
        # En cas d'erreur, on peut logger ou afficher un message
        return 0

    data = response.json()
    created_count = 0
    for item in data['results'][:10]:   
        obj, created = Series.objects.get_or_create(
            tmdb_id=item['id'],
            user=request.user,
            defaults={
                'name': item['name'],
                'overview': item.get('overview', ''),
                'poster_path': item.get('poster_path', ''),
                'vote_average': item.get('vote_average', 0.0),
                'provider': provider_name,
            }
        )
        if created:
            created_count += 1

    # Mise à jour de la page dans la session pour le prochain clic
    if request:
        total_pages = data.get('total_pages', 1)
        if page < total_pages:
            request.session[page_key] = page + 1
        else:
            # Si on a atteint la dernière page, on recommence à 1
            request.session[page_key] = 1

    return created_count

def add_netflix(request):
    fetch_and_save_series('netflix', 8, request=request)
    return redirect('watchlist')

def add_prime(request):
    fetch_and_save_series('prime', 9, request=request)
    return redirect('watchlist')

def add_apple(request):
    fetch_and_save_series('apple', 2, request=request)
    return redirect('watchlist')

def add_action(request):
    # Pour les séries d'action, on utilise le genre 10759, sans fournisseur
    fetch_and_save_series('action', None, genre_id=10759, request=request)
    return redirect('watchlist')

# ...existing code...
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connecte l'utilisateur après inscription
            return redirect("list")  # Redirige vers la page principale
    else:
        form = UserCreationForm()
    return render(request, "series/register.html", {"form": form})
# ...existing code...

@login_required
def delete_series(request, series_id):
    serie = Series.objects.get(id=series_id, user=request.user)
    serie.delete()
    return redirect('watchlist')

@login_required
def watchlist(request):
    """Affiche toutes les séries de la watchlist"""
    series_list = Series.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'watchlist.html', {'series_list': series_list})