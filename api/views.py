from django.shortcuts import render
from rest_framework import viewsets

from .models import Recipes, CustomUser
from .serializers import RecipesSerializer, CustomUserSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset=CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all()
    serializer_class = RecipesSerializer
