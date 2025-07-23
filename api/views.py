from django.shortcuts import render
from rest_framework import viewsets

from .models import Recipes, CustomUser
from .serializers import RecipesSerializer, CustomUserSerializer

from login_required import login_not_required


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all()
    serializer_class = RecipesSerializer
     
@login_not_required   
class RegisterViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    
class LoginViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer
