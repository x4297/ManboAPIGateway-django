from django.urls import path

from . import views


urlpatterns = [
    path('searchByPrefix/', views.SearchUPUsersByPrefix.as_view()),
    path("enable/", views.EnableUPUser.as_view()),
    path("changePhone/", views.ChangePhone.as_view()),
]
