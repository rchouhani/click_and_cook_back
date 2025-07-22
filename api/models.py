from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class CustomUsers(AbstractBaseUser):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Recipes(models.Model):
    title = models.CharField(max_length=255)
    cook_time_min = models.IntegerField()
    prep_time_min = models.IntegerField()
    servings = models.IntegerField()
    user = models.ForeignKey(CustomUsers, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
class Ingredients(models.Model):
    title = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unity = models.CharField(max_length=12)
    recipe = models.ForeignKey(Recipes, related_name="ingredients", on_delete=models.DO_NOTHING)
    

class Follows(models.Model):
    following_user= models.ForeignKey(CustomUsers, on_delete=models.DO_NOTHING)
    followed_user= models.ForeignKey(CustomUsers, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    
class Likes(models.Model):
    user = models.ForeignKey(CustomUsers, on_delete=models.DO_NOTHING)
    recipe = models.ForeignKey(Recipes, on_delete=models.DO_NOTHING)
    

class Steps(models.Model):
    description = models.CharField()
    recipe = models.ForeignKey(Recipes, related_name="steps", on_delete=models.DO_NOTHING)