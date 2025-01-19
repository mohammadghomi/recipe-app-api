"""
Serializers for recipe APIs
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes"""
    tags = TagSerializer(many=True, required=False)
    ingredient = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ["id", "title", "time_minutes", "price", "link", "tags", "ingredient"]
        read_only_fields = ["id"]

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags needed."""
        auth_user = self.context["request"].user
        for tag in tags:
            tag_obj , created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredient, recipe):
        """Handle getting or creating ingredeints needed."""
        auth_user = self.context["request"].user
        for ingredients in ingredient:
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredients
            )
            recipe.ingredient.add(ingredient_obj)

    def create(self, validated_data):
        """create a recipe."""
        tags = validated_data.pop("tags", [])
        ingredients = validated_data.pop("ingredient", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop("tags", None)
        ingredient = validated_data.pop("ingredient", None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredient is not None:
            instance.ingredient.clear()
            self._get_or_create_ingredients(ingredient, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """serializer for recipe detail view"""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description", "image"]


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading image to recipes."""

    class Meta:
        model = Recipe
        fields = ["id", "image"]
        read_only_fields = ["id"]
        extra_kwargs = {"image": {"required": "True"}}
