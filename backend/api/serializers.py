import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class Base64Image(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, encoded_str = data.split(';base64,')
            file_ext = header.split('/')[-1]
            data = ContentFile(
                base64.b64decode(encoded_str),
                name=f'temp.{file_ext}'
            )
        return super().to_internal_value(data)


class UserSerializer(DjoserUserSerializer):
    """Сериализатор пользователя с доп. полем подписки."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if current_user.is_anonymous:
            return False
        return obj.subscribing.filter(user=current_user).exists()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64Image()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsReaderSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов внутри рецепта."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения списка рецептов."""
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientsReaderSerializer(
        source='recipe_ingredients', many=True
    )
    image = Base64Image()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreatingSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецепта."""
    ingredients = serializers.ListField()
    image = Base64Image()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        if not ingredients_data:
            raise serializers.ValidationError(
                {'ingredients': 'Список ингредиентов не может быть пустым.'}
            )
        unique_ids = set()
        for item in ingredients_data:
            ing_id = item.get('id')
            amount = item.get('amount')

            if not Ingredient.objects.filter(id=ing_id).exists():
                raise serializers.ValidationError(
                    {'ingredients': f'Ингредиент с id={ing_id} не найден.'}
                )
            if ing_id in unique_ids:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты не должны повторяться.'}
                )
            unique_ids.add(ing_id)

            if int(amount) <= 0:
                raise serializers.ValidationError(
                    {'amount': 'Количество должно быть положительным числом.'}
                )

        if data.get('cooking_time') <= 0:
            raise serializers.ValidationError(
                {'cooking_time': 'Время приготовления должно быть > 0.'}
            )

        return data

    def save_ingredients(self, ingredients_list, recipe):
        records = []
        for ingredient in ingredients_list:
            records.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount']
                )
            )
        RecipeIngredient.objects.bulk_create(records)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.save_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self.save_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Укороченный рецепт."""
    image = Base64Image()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    """Сериализатор выдачи подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count',
            'avatar'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except ValueError:
                pass
        return RecipeMiniSerializer(
            queryset, many=True, context={'request': request}
        ).data
