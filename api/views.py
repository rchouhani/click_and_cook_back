from django.shortcuts import render
from rest_framework import viewsets, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate

from .models import Recipes, CustomUser, Likes, Follows
from .serializers import RecipesSerializer, CustomUserSerializer, LikesSerializer, FollowsSerializer


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
    
    
class LikeViewSet(viewsets.ModelViewSet):
    queryset = Likes.objects.all()
    serializer_class = LikesSerializer
    
    def create(self, request):
        user =  request.data.get('user')
        recipe = request.data.get('recipe')
        
        like, created = Likes.objects.get_or_create(user_id=user, recipe_id=recipe)
        if not created:
            return Response({'Déjà liké'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
class FollowsViewSet(viewsets.ModelViewSet):
    serializer_class = FollowsSerializer


    def get_queryset(self):
        user = self.request.user

        return Follows.objects.filter(user=user)

    def create(self, request):
        following_user = request.data.get('following_user')
        followed_user = request.data.get('followed_user')

        follow, created = Follows.objects.get_or_create(following_user_id=following_user, followed_user_id=followed_user)
        if not created:
            return Response({'Tu ne peux pas suivre un utilisateur deux fois'}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
