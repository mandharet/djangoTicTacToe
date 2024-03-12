from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from apps.game import forms
from apps.game import models

# Create your views here.
def index(request):
    if request.method == "POST":
        form = forms.NewGameForm(request.POST)
        if form.is_valid():
            # Create a new room with vacant as True
            new_room = models.Room.objects.create(vacant=True)
            
            # Save the player's name and associate it with the new room
            player_name = form.cleaned_data['name']
            new_player = models.Player.objects.create(name=player_name, shared_room=new_room)

            # Redirect to the waiting view with the room ID as an argument
            return redirect('waiting', room_id=new_room.id)
    else:
        form = forms.NewGameForm()
    
    return render(request, "games/game.html", {"form": form})


def waiting(request, room_id):
    room = get_object_or_404(models.Room, id=room_id)
    players_in_room = models.Player.objects.filter(room=room)

    if request.method == "POST":
        # Handle the form submission for the second player
        form = forms.NewGameForm(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['name']
            new_player = models.Player.objects.create(name=player_name, shared_room=room)
            return redirect('game', room_id=room.id)  # Redirect to the game view
    else:
        form = forms.NewGameForm()

    return render(request, "waiting.html", {"room": room, "players": players_in_room, "form": form})