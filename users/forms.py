from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class StockForm(forms.Form):
    ticker = forms.CharField(label="Search Ticker Here", max_length=4)

class BuyForm(forms.Form):
    buy = forms.IntegerField(label="Buy Stock")

class SellForm(forms.Form):
    sell = forms.IntegerField(label="Sell Stock")
