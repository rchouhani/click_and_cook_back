from django.shortcuts import render
from rest_framework import viewsets, serializers, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
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
        

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
     user = request.user
     return Response({
        "user": {
            "username": user.username,
        }
    })
    

class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all().order_by('-created_at')[:3]
    serializer_class = RecipesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['created_at']    


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
                "auth_token": token.key,
                "message": "Connexion Réussie",
                "user": {
                "username": user.username,
                "id": user.id,
                }
        })
        
        response.set_cookie(
            # "auth_token",
            # token.key,
            key='auth_token',
            value=token.key,
            max_age=3600,
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        return response
    
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        deleted_token = Token.objects.get(user = request.user)
        deleted_token.delete()
        return Response({'Vous êtes déconnecté'}, status=status.HTTP_200_OK)
    
    
class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikesSerializer

    def get_queryset(self):
        user = self.request.user
        return Likes.objects.filter(user=user)
    
    def create(self, request):
        user =  request.user
        recipe = request.data.get('recipe')
        
        like, created = Likes.objects.get_or_create(user=user, recipe_id=recipe)
        if not created:
            return Response({'Déjà liké'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        
    def destroy(self, request, pk=None):
        user = request.user
        recipe = request.data.get('recipe')
        
        deleted_like = Likes.objects.get(user=user, recipe_id=recipe)
        deleted_like.delete()
        return Response({"Tu viens d'unlike"}, status=status.HTTP_200_OK)
            
        
class FollowsViewSet(viewsets.ModelViewSet):
    serializer_class = FollowsSerializer


    def get_queryset(self):
        user = self.request.user

        return Follows.objects.filter(following_user=user)

    def create(self, request):
        following_user = request.user
        followed_user = request.data.get('followed_user')
        
        follow, created = Follows.objects.get_or_create(following_user=following_user, followed_user_id=followed_user)
        if not created:
            return Response({'Tu ne peux pas suivre un utilisateur deux fois'}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = self.get_serializer(follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    
    def destroy(self, request, pk=None):
         following_user = request.user
         followed_user = request.data.get('followed_user')
        
         deleted_follow = Follows.objects.get(following_user=following_user, followed_user_id=followed_user)
         deleted_follow.delete()
         return Response({"Tu viens d'unfollow"}, status=status.HTTP_200_OK)