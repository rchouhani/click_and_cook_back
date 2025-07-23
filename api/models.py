from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Nom d'utilisateur requis")
        if not password:
            raise ValueError("Mot de passe requis")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'username'
    objects = CustomUserManager()
    

class Recipes(models.Model):
    title = models.CharField(max_length=255)
    cook_time_min = models.IntegerField()
    prep_time_min = models.IntegerField()
    servings = models.IntegerField()
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    picture = models.CharField(max_length=1024)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Ingredients(models.Model):
    title = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unity = models.CharField(max_length=12)
    recipe = models.ForeignKey(Recipes, related_name="ingredients", on_delete=models.CASCADE)
    

class Follows(models.Model):
    following_user= models.ForeignKey(CustomUser, related_name='following', on_delete=models.CASCADE)
    followed_user= models.ForeignKey(CustomUser, related_name='followed', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    
class Likes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, related_name='likes', on_delete=models.CASCADE)
    

class Steps(models.Model):
    description = models.CharField()
    recipe = models.ForeignKey(Recipes, related_name="steps", on_delete=models.CASCADE)