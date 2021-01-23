from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import CustomUserCreationForm, StockForm, BuyForm, SellForm
from users.models import User, Stocks
from yahoo_fin import stock_info as si

from decimal import *

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
            trader = User.objects.get(pk=user_id)

            # This idea is a fucking twat idea
            # if(trader != None):
            #     money = trader.money - int(stockJSON)
            #     trader.money = money
                
            # stockJSON = trader.money
            
            request.session['ticker'] = stockTicker
            request.session['stock_info'] = stockJSON
            request.session['trader_name'] = trader.name
            request.session['trader_money'] = locale.currency(trader.money, grouping=True)
            request.session['display'] = ' '
            if(len(Stocks.objects.filter(pk=user_id)) == 0):
                request.session['stocks_owned'] = 0
            else:
                request.session['stocks_owned'] = Stocks.objects.filter(pk=user_id)[0].amount
            
            return redirect("viewStock", user_id)

def viewStock(request, user_id):
    locale.setlocale(locale.LC_ALL, '')
    context = {
        'stock_info': request.session['stock_info'],
        'trader_name': request.session['trader_name'],
        'trader_money': request.session['trader_money'],
        'buy_form': BuyForm,
        'sell_form' : SellForm,
        'display': request.session['display'],
        'amount_owned': request.session['stocks_owned']
    }

    if request.method == "GET":
        return render(request, "users/ViewStock.html", context)
    elif request.method == "POST":

        if('sell_button' in request.POST):
            form = SellForm(request.POST)
            if form.is_valid():
                stock_price = request.session['stock_info']
                trader = User.objects.get(pk=user_id)
                money = trader.money
                quantity = form["sell"].value()
                if(len(Stocks.objects.filter(pk=user_id)) != 0):
                    amount = Stocks.objects.filter(ticker = request.session['ticker'], pk=user_id)[0].amount
                    if(int(quantity) > amount):
                        request.session['display'] = "You don't own enough of this stock"
                    else:
                        
                        stock_price = stock_price.strip(',')
                        stock_price = stock_price.strip('$')
                        money = trader.money + Decimal((float(quantity) * float(stock_price)))
                        row = Stocks.objects.filter(pk=user_id)[0]
                        new_amount = Stocks.objects.filter(pk=user_id)[0].amount - int(quantity)
                        row.amount = new_amount
                        row.save()
                        trader.money = money
                        trader.save()
                        request.session['trader_money'] = locale.currency(trader.money, grouping=True)
                        # Set context trader_money (locale)
                        context['trader_money'] = request.session['trader_money']
                        request.session['stocks_owned'] = Stocks.objects.filter(pk=user_id)[0].amount
            else:
                request.session['display'] = "You don't own this stock"
            
        else:
            form = BuyForm(request.POST)
            if form.is_valid():
                stock_price = request.session['stock_info']
                trader = User.objects.get(pk=user_id)
                money = trader.money

                print(money)

                quantity = form["buy"].value()
                
                stock_price = stock_price.strip(',')
                stock_price = stock_price.strip('$')

                money = trader.money - Decimal((float(quantity) * float(stock_price)))
                
                if(money < 0):
                    request.session['display'] = "Inefficient funds to purchase"
                    return redirect("viewStock", user_id)
                else:
                    request.session['display'] = "Succesfully bought"
                    trader.money = money
                    trader.save()
                    
                    if(len(Stocks.objects.filter(pk=user_id)) == 0):
                        amount_stock = 0
                        stocks = Stocks(ticker = request.session['ticker'], owned_by = trader, amount = int(amount_stock) + int(quantity))
                        stocks.save()   
                    else:
                        row = Stocks.objects.filter(pk=user_id)[0]
                        new_amount = Stocks.objects.filter(pk=user_id)[0].amount + int(quantity)
                        row.amount = new_amount
                        row.save()
                        
                    
                    # Set request session's tradermoney (global)
                    request.session['trader_money'] = locale.currency(trader.money, grouping=True)

                    # Set context trader_money (locale)
                    context['trader_money'] = request.session['trader_money']
                    request.session['stocks_owned'] = Stocks.objects.filter(pk=user_id)[0].amount
                    
    return redirect("viewStock", user_id)



def buyStock(request, user_id):
    pass

