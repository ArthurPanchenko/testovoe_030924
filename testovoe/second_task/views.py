from django.shortcuts import render

from .models import PlayerLevel

def export_players_level(request):
    response = PlayerLevel.export_to_csv()
    return response