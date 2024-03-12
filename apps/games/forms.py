#! -*- coding: utf-8 -*-

from django import forms
from . import models


class NewGameForm(forms.ModelForm):
    size = forms.IntegerField(min_value=3, max_value=10, initial=3)
    min_length = forms.IntegerField(min_value=3, max_value=10, initial=3)

    class Meta:
        model = models.Game
        fields = 'size', 'min_length', 'allow_horizontal', 'allow_vertical', 'allow_diagonal',

    def clean(self):
        data = super(NewGameForm, self).clean()
        if not any([data['allow_horizontal'], data['allow_vertical'], data['allow_diagonal']]):
            raise forms.ValidationError('You should allow at least one direction')
        if data['size'] < data['min_length']:
            raise forms.ValidationError('The minimum length should be less than or equal to the size')
        return data
