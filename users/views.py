from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm, StockForm
from users.models import User, Stocks
from yahoo_fin import stock_info as si


import yfinance as yf

def dashboard(request):
    return render(request, "users/dashboard.html")

def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Shove in user_auth
            user = form.save()
            
            # Shove in user 
            new_user = User(name=user.username, money=100000)
            new_user.save()

            login(request, user)

            return redirect(reverse("dashboard"))

def searchStock(request):
    if request.method == "GET":
        return render(request, "users/searchStock.html", {"form": StockForm})
    elif request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stockTicker = form["ticker"].value()
            stockJSON = si.get_live_price(stockTicker)

            #find corresponding user and take awayy money spent
            username = str(request.user)
            # print(trader)
            # print(trader.name)
            trader = None
            for user in User.objects.all():
                print(username)
                print(type(user.name))
                print(user.money)
                if(user.name == username):
                    print("sadsdfg")
                    trader = user
            print(trader.name)
            print(trader.money)
            if(trader != None):
                money = trader.money - int(stockJSON)
                trader.money = money
                
            stockJSON = trader.money
            

            return redirect("viewStock", stockJSON)

def viewStock(request, stockJSON):
    context = {'stock_info': stockJSON}
    return render(request, "users/viewStock.html", context)