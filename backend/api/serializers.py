import base64

from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import Ingredient, Recipe, RecipeIngredient
from rest_framework import serializers
from users.models import User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if not hasattr(obj, 'subscribing'):
                return False
            return obj.subscribing.filter(user=request.user).exists()
        return False


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.favorites.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.shopping_cart.filter(recipe=obj).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'image', 'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_list = []
        for item in ingredients:
            try:
                ingredient = Ingredient.objects.get(id=item['id'])
            except Ingredient.DoesNotExist:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиент не существует!'
                })
            if ingredient in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Ингредиенты не могут повторяться!'
                })
            ingredients_list.append(ingredient)
            if int(item['amount']) < 1:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })

        cooking_time = data.get('cooking_time')
        if int(cooking_time) < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления не менее 1 минуты!'
            })

        return data

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            )
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.save()
        instance.recipe_ingredients.all().delete()
        self.create_ingredients(ingredients, instance)
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscriptionsSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count',
                  'avatar')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(
            recipes, many=True, context={'request': request}
        ).data
