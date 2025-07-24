from django.shortcuts import render
from rest_framework import viewsets, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import Recipes, CustomUser
from .serializers import RecipesSerializer, CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        else: 
            return [IsAuthenticated()]


class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all()
    serializer_class = RecipesSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]
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
                "id": user.id,
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