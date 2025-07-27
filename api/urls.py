from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipesViewSet, CustomUserViewSet, CurrentUserView, LoginView, LogoutView, LikeViewSet, FollowsViewSet

router = DefaultRouter()

router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'user', CustomUserViewSet, basename='user')
router.register(r'likes', LikeViewSet, basename='likes')
router.register(r'follows', FollowsViewSet, basename='follows')

urlpatterns = [
    path('api/', include(router.urls)),
    path('user/me/', CurrentUserView.as_view(), name='current-user'),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
]
