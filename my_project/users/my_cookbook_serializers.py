from rest_framework import serializers
from .models import MyCookbook, Recipe

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['recipe_id', 'title', 'description', 'cook_time']  # Add other relevant fields as needed

class MyCookbookSerializer(serializers.ModelSerializer):
    recipes = RecipeSerializer(many=True, read_only=True)
    recipe_ids = serializers.ListField(
        child=serializers.ObjectIdField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = MyCookbook
        fields = [
            'cookbook_id', 'name', 'description', 'recipes', 
            'recipe_ids', 'created_at', 'updated_at', 'is_public'
        ]
        read_only_fields = ['cookbook_id', 'created_at', 'updated_at', 'recipes']

    def create(self, validated_data):
        recipe_ids = validated_data.pop('recipe_ids', [])
        owner = self.context['request'].user  # Assuming the user is available in the request context
        cookbook = MyCookbook(owner=owner, **validated_data)
        cookbook.save()
        if recipe_ids:
            recipes = Recipe.objects.filter(recipe_id__in=recipe_ids)
            cookbook.recipes.extend(recipes)
            cookbook.save()
        return cookbook

    def update(self, instance, validated_data):
        recipe_ids = validated_data.pop('recipe_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if recipe_ids:
            recipes = Recipe.objects.filter(recipe_id__in=recipe_ids)
            instance.recipes.extend(recipes)
        instance.save()
        return instance
