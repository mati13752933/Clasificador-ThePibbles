from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Perfil


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500",
                "placeholder": "Nombre de usuario"
            })
        }


class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ["foto"]

        widgets = {
            "foto": forms.ClearableFileInput(attrs={
                "class": "w-full text-gray-700 p-2 bg-white rounded-xl border border-gray-300 file:mr-5 file:border-0 file:bg-teal-500 file:px-5 file:py-2 file:rounded-lg file:text-white file:cursor-pointer hover:file:bg-teal-700"
            })
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        for campo in self.fields.values():
            campo.widget.attrs.update({
                "class": "w-full border border-gray-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500"
            })