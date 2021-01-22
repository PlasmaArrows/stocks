from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class StockForm(forms.Form):
    ticker = forms.CharField(label="GME TO THE FUCKING MOON", max_length=4)

class BuyForm(forms.Form):
    buy = forms.IntegerField(label="Buy Stock")
