from django import forms
from .models import CustomUser

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['password', 'first_name', 'last_name', 'university', 'college', 'major', 'birth', 'phone_number', 'email']