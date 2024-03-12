from django import forms
from . import models


class NewGameForm(forms.Form):
    name = forms.CharField(label="Enter Name", max_length=10)

    class Meta:
        model = models.Player
        fields = 'name',

    def clean(self):
        data = super(NewGameForm, self).clean()
        if data['name'] == "":
            raise forms.ValidationError('Please Enter Name')
        return data