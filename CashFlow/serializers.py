from rest_framework import serializers
from .models import Logs, Status, Type, Category, Subcategory, Comments

class StatusSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Status."""
    class Meta:
        model = Status
        fields = ['id', 'name']

class TypeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Type."""
    class Meta:
        model = Type
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        model = Category
        fields = ['id', 'name']

class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subcategory с категорией."""
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']

class LogSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения логов с отображением названий, а не ID."""
    status = serializers.SlugRelatedField(slug_field='name', read_only=True)
    type = serializers.SlugRelatedField(slug_field='name', read_only=True)
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    subcategory = serializers.SlugRelatedField(slug_field='name', read_only=True)
    comment = serializers.SlugRelatedField(slug_field='content', read_only=True)

    class Meta:
        model = Logs
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']

class PostLogSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления логов с передачей ID связанных сущностей."""
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())
    comment = serializers.PrimaryKeyRelatedField(queryset=Comments.objects.all())
    amount = serializers.FloatField()

    class Meta:
        model = Logs
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
