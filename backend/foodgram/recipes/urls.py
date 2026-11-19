from django.urls import path

from recipes.views import redirect_short_link

app_name = "recipes"

urlpatterns = [
    path("s/<str:short_link>/", redirect_short_link, name="short-link"),
]
