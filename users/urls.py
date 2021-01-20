# users/urls.py

from django.conf.urls import include, url
from users.views import dashboard, register, searchStock, viewStock

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^dashboard/", dashboard, name="dashboard"),
    url(r"^register/", register, name="register"),
    url(r"^searchStock/", searchStock, name="search_stock"),
    url(r"^viewStock/(.*)", viewStock, name="viewStock")
]
