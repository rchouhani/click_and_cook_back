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
        fields = ['id','firstname', 'lastname', 'email', 'username', 'password']
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance,attr, value)
        
        if password:
            instance.set_password(password)

        instance.save()
        return instance
 
        
class RecipesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    ingredients = IngredientsSerializer(many = True)
    steps = StepsSerializer(many = True)
    user_detail = CustomUserSerializer(source='user', read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'title', 'cook_time_min', 'prep_time_min', 'servings','ingredients','steps','picture','likes_count','is_liked', 'user', 'user_detail', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()    
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            return  obj.likes.filter(user=user).exists()
        return False

    def create(self, validated_data):
        # request = self.context.get('request')
        ingredients_data = validated_data.pop('ingredients')        
        steps_data = validated_data.pop('steps')
        
        # user = request.user if request else None
        
        # if not user or not user.is_authenticated:
        #     raise serializers.ValidationError('Utilisateur non authentifié.')
        
        recipe = Recipes.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            Ingredients.objects.create(recipe=recipe, **ingredient_data)
            
        for step_data in steps_data:
            Steps.objects.create(recipe=recipe, **step_data)
            
        return recipe
 
    
class LikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = '__all__'
        
            
class FollowsSerializer(serializers.ModelSerializer):
    following_user_detail = CustomUserSerializer(source='following_user', read_only=True)
    followed_user_detail = CustomUserSerializer(source='followed_user', read_only=True)
    
    class Meta:
        model = Follows
        fields = ['following_user', 'followed_user_detail', 'following_user_detail']