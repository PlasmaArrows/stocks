# users/urls.py

from django.conf.urls import include, url
from users.views import dashboard, register, searchStock, viewStock

urlpatterns = [
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(r"^dashboard/", dashboard, name="dashboard"),
    url(r"^register/", register, name="register"),
    url(r"^searchStock/(?P<user_id>[\d]+)/", searchStock, name="search_stock"),
    url(r"^viewStock/(?P<user_id>[\d]+)/", viewStock, name="viewStock"),
]
