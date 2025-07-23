from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipesViewSet, CustomUserViewSet

router = DefaultRouter()

router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'user', CustomUserViewSet, basename='user')

urlpatterns = [
    path('api/', include(router.urls))
]
