from django.shortcuts import render
from rest_framework import viewsets, serializers, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
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
        
    @action(detail=False, methods=['get'], url_path='username/(?P<username>[^/.]+)')
    def by_username(self, request, username=None):
        user = get_object_or_404(CustomUser, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='profile')
    def profile_with_stats(self, request, pk=None):
        user = self.get_object()
        
        recipes_count = Recipes.objects.filter(user=user).count()
        followers_count = Follows.objects.filter(followed_user=user).count()
        following_count = Follows.objects.filter(following_user=user).count()
        total_likes = Likes.objects.filter(recipe__user=user).count()
        
        is_followed = False
        if request.user.is_authenticated:
            is_followed = Follows.objects.filter(
                following_user=request.user, 
                followed_user=user
            ).exists()
        
        serializer = self.get_serializer(user)
        data = serializer.data
        
        data.update({
            'recipes_count': recipes_count,
            'followers_count': followers_count,
            'following_count': following_count,
            'total_likes_received': total_likes,
            'is_followed': is_followed,
        })
        
        return Response(data)
        

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at,
            }
    })
    

class RecipesViewSet(viewsets.ModelViewSet):
    queryset= Recipes.objects.all().order_by('-created_at')
    serializer_class = RecipesSerializer
    permission_classes = [AllowAny]
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['created_at']
    
    def get_serializer_context(self):
        return {'request': self.request}
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)')
    def by_user(self, request, user_id=None):
        """Récupère les recettes d'un utilisateur spécifique"""
        user = get_object_or_404(CustomUser, id=user_id)
        recipes = self.queryset.filter(user=user)
        
        # SI BESOIN DE METTRE LA PAGINATION : 
        # page = self.paginate_queryset(recipes)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='liked-by/(?P<user_id>[^/.]+)')
    def liked_by_user(self, request, user_id=None):
        """Récupère les recettes likées par un utilisateur spécifique (par ID)"""
        user = get_object_or_404(CustomUser, id=user_id)
        
        liked_recipes = self.queryset.filter(likes__user=user).distinct()
        
        page = self.paginate_queryset(liked_recipes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(liked_recipes, many=True)
        return Response(serializer.data)
    



class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        
        origin = request.META.get('HTTP_ORIGIN')
        print("Origin reçue :", origin)
        
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            raise serializers.ValidationError("Nom d’utilisateur incorrect")
        
        if not user.check_password(password):
            raise serializers.ValidationError("Mot de passe incorrect")
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "auth_token": token.key,
            "message": "Connexion réussie",
            "user": {
                "username": user.username,
                "id": user.id,
            }
        })
    
    
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
        recipe_id = pk
        
        try:
            like_to_delete = Likes.objects.get(user=user, recipe_id=recipe_id)
            like_to_delete.delete()
            return Response({"message": "Le like a bien été supprimé"}, status=status.HTTP_204_NO_CONTENT)
        except Likes.DoesNotExist:
            return Response({"error": "Like non trouvé"}, status=status.HTTP_404_NOT_FOUND)


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
    
    @action(detail=False, methods=['get'], url_path='user-followers/(?P<user_id>[^/.]+)')
    def user_followers(self, request, user_id=None):
        user = get_object_or_404(CustomUser, id=user_id)
        
        followers = Follows.objects.filter(followed_user=user).select_related('following_user')
        
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)