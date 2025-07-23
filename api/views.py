from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Recipes, CustomUser
from .serializers import RecipesSerializer, CustomUserSerializer

# from login_required import login_not_required

# @login_not_required
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all()
    serializer_class = RecipesSerializer


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is None:
                raise serializers.ValidationError("Email incorrect")
        
        if not user.check_password(password):
            raise serializers.ValidationError("mot de passe incorrect")
        
        
        token, created = Token.objects.get_or_create(user=user)
        response = Response ({
                "message": "Connexion Réussie",
                "user": {
                "username": user.username,
                "password": user.password,
                }
        })
        
        response.set_cookie(
            "auth_token",
            token.key,
            max_age=3600,
            httponly=True,
            secure=False,
            samesite="Strict"
        )
        return response     