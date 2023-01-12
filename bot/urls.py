from django.urls import path

from bot import views

urlpatterns = [
    path('verify', views.VerifyTgBotView.as_view(), name="bot_verify"),
]
