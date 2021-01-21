from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm, StockForm
from users.models import User, Stocks
from yahoo_fin import stock_info as si

import locale

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

def searchStock(request, user_id):
    if request.method == "GET":
        return render(request, "users/searchStock.html", {"form": StockForm})
    elif request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():

            locale.setlocale(locale.LC_ALL, '')

            stockTicker = form["ticker"].value()
            stockJSON = locale.currency(si.get_live_price(stockTicker), grouping=True)
            

            # FIX LATER
            trader = User.objects.get(pk=int(user_id) - 3)

            # This idea is a fucking twat idea
            # if(trader != None):
            #     money = trader.money - int(stockJSON)
            #     trader.money = money
                
            # stockJSON = trader.money
            
            request.session['stock_info'] = stockJSON
            request.session['trader_name'] = trader.name
            request.session['trader_money'] = locale.currency(trader.money, grouping=True)

            return redirect("viewStock", user_id)

def viewStock(request, user_id):
    context = {
        'stock_info': request.session['stock_info'],
        'trader_name': request.session['trader_name'],
        'trader_money': request.session['trader_money'],
    }


    return render(request, "users/viewStock.html", context)

def buyStock(request):
    pass