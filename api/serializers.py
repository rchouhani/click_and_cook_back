from rest_framework import serializers
from .models import CustomUser, Recipes, Ingredients, Follows, Likes, Steps

class StepsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Steps
        fields = ['id', 'description']
        

class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ['title', 'quantity', 'unity']
        
        
class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['firstname', 'lastname', 'email', 'username', 'password']
        
        
class RecipesSerializer(serializers.ModelSerializer):
    ingredients = IngredientsSerializer(many = True)
    steps = StepsSerializer(many = True)
    user_detail = CustomUserSerializer(source='user', read_only=True)
    class Meta:
        model = Recipes
        fields = ['title', 'cook_time_min', 'prep_time_min', 'servings', 'user', 'user_detail']
        
    def create(self, validated_data):
        ingredients_data = validated_data.pop(Ingredients)        
        steps_data = validated_data.pop(Steps)
        
        recipe = Recipes.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            Ingredients.objects.create(recipe=recipe, **ingredient_data)
            
        for step_data in steps_data:
            Steps.objects.create(recipe=recipe, **step_data)
            
        return recipe