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

            # Retrieve stock ticker from form and stock price from API
            stock_ticker = form["ticker"].value().upper()
            stock_price = si.get_live_price(stock_ticker)
            stock_price_formatted = locale.currency(stock_price, grouping=True)

            # Retrieve current trader from db
            user = User.objects.get(pk=user_id)

            # Set session variables to be used in other functions/pages 
            request.session['stock_ticker'] = stock_ticker
            request.session['stock_price'] = stock_price
            request.session['stock_price_formatted'] = stock_price_formatted
            request.session['user_name'] = user.name
            request.session['user_money_formatted'] = locale.currency(user.money, grouping=True)
            request.session['display'] = ''

            # If the user does NOT own the current stock 
            if len(Stocks.objects.filter(owned_by__pk=user_id, ticker=stock_ticker)) == 0:
                request.session['quantity_owned'] = 0

            # If the user owns the current stock
            else:
                request.session['quantity_owned'] = Stocks.objects.filter(owned_by__pk=user_id, 
                    ticker=stock_ticker)[0].quantity_owned
            
            return redirect("viewStock", user_id)

def viewStock(request, user_id):
    # Set variables to be used in html page
    context = {
        'stock_ticker': request.session['stock_ticker'],
        'stock_price': request.session['stock_price'],
        'stock_price_formatted': request.session['stock_price_formatted'],
        'user_name': request.session['user_name'],
        'user_money_formatted': request.session['user_money_formatted'],
        'quantity_owned': request.session['quantity_owned'],
        'buy_form': BuyForm,
        'sell_form' : SellForm,
        'display': request.session['display'],
    }

    print(user_id)
    print(Stocks.objects.filter(owned_by__pk=user_id))
    print(user_id)
    print(User.objects.filter(pk=user_id))

    if request.method == "GET":
        return render(request, "users/ViewStock.html", context)
    elif request.method == "POST":

        locale.setlocale(locale.LC_ALL, '')

        # User BUYS stock
        if 'buy_button' in request.POST:    
            form = BuyForm(request.POST)
            quantity = int(form["buy"].value())

            if form.is_valid() and quantity > 0:
                
                # Retrieve current user
                user = User.objects.get(pk=user_id)
                user_money = user.money

                # Calculate total cost
                stock_price = request.session['stock_price']
                total_cost = Decimal(quantity) * Decimal(stock_price)

                # Ensure user has enough money
                user_money -= total_cost

                if user_money < 0:
                    request.session['display'] = "Insufficient funds!"
                    return redirect("viewStock", user_id)
                else:
                    request.session['display'] = "Successfully bought!"
                    user.money = user_money
                    user.save()

                    stock_ticker = request.session['stock_ticker']

                    print(stock_ticker)
                    # User does NOT own any shares of current stock
                    if len(Stocks.objects.filter(owned_by__pk=user_id, ticker=stock_ticker)) == 0:
                        print("REACHED INSIDE HERE")
                        add_stock = Stocks(ticker=stock_ticker, 
                            owned_by = user, 
                            quantity_owned = quantity)
                        add_stock.save()

                        print("hellow")

                    # User owns shares of current stock
                    else:
                        update_stock = Stocks.objects.filter(
                            owned_by__pk=user_id, 
                            ticker=stock_ticker)[0]
                        new_quantity = update_stock.quantity_owned + quantity
                        update_stock.quantity_owned = new_quantity
                        update_stock.save()

                    # Update session variables
                    request.session['user_money_formatted'] = locale.currency(
                        user.money, grouping=True)

                    request.session['quantity_owned'] = Stocks.objects.filter(owned_by__pk=user_id, 
                        ticker=stock_ticker)[0].quantity_owned

                    # Update context variables
                    context['user_money_formatted'] = request.session['user_money_formatted']

                    return redirect("viewStock", user_id)

            # Quantity is negative
            else:
                return redirect("viewStock", user_id)

        # User SELLS stock
        else:
            form = SellForm(request.POST)
            quantity = int(form["sell"].value())

            if form.is_valid() and quantity > 0:

                # Retrieve current user
                user = User.objects.get(pk=user_id)
                user_money = user.money

                # Ensure user has enough shares to sell
                stock_ticker = request.session['stock_ticker']

                # User does NOT own current stock
                if len(Stocks.objects.filter(owned_by__pk=user_id, ticker=stock_ticker)) == 0:
                    request.session['display'] = "You do not own this stock!"
                    return redirect("viewStock", user_id)

                # User owns current stock
                else:
                    curr_stock_entry = Stocks.objects.filter(owned_by__pk=user_id, ticker=stock_ticker)[0]
                    curr_quantity_owned = curr_stock_entry.quantity_owned
                   
                    # User wants to sell more than quantity owend
                    if quantity > curr_quantity_owned:
                        request.session['display'] = "You do not own enough of this stock!"
                        return redirect("viewStock", user_id)
                    
                    # Valid 
                    else:

                        # Update user money
                        stock_price = request.session['stock_price']
                        total = Decimal(quantity) * Decimal(stock_price)
                        user_money += total
                        user.money = user_money
                        user.save()
                        request.session['user_money_formatted'] = locale.currency(user.money, grouping=True)
                        context['user_money_formatted'] = request.session['user_money_formatted']

                        # Update stocks
                        curr_quantity_owned -= quantity

                        if curr_quantity_owned == 0:
                            curr_stock_entry.delete()

                        else:
                            curr_stock_entry.quantity_owned = curr_quantity_owned
                            curr_stock_entry.save()

                        request.session['quantity_owned'] = curr_quantity_owned

                        return redirect("viewStock", user_id)

            # Quantity is negative
            else:
                return redirect("viewStock", user_id)
