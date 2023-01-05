from django.shortcuts import redirect
from rest_framework.generics import GenericAPIView

URL_NAME = "https://oauth.vk.com/authorize?"
client_id = "client_id=51519338"
scope = "scope=email"
redirect_uri = "http://127.0.0.1:9999/callback"


class AuthVKView(GenericAPIView):
    redirect(URL_NAME + client_id + scope + redirect_uri)
