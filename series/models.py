from django.db import models
from django.contrib.auth.models import User

class Series(models.Model):
    tmdb_id = models.IntegerField(unique=True)          # ID unique TMDB pour éviter les doublons
    name = models.CharField(max_length=200)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=200, blank=True)   # chemin relatif (ex: /abcd.jpg)
    vote_average = models.FloatField(default=0)
    provider = models.CharField(max_length=50)           # 'netflix', 'prime', 'apple', ou 'action'
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name