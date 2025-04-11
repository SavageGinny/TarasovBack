from rest_framework import serializers
from .models import Logs, Status, Type, Category, Subcategory, Comments

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'name']

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class SubcategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']

class LogSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    type = serializers.CharField()
    category = serializers.CharField()
    subcategory = serializers.CharField()
    comment = serializers.CharField()

    class Meta:
        model = Logs
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']

class PostLogSerializer(serializers.ModelSerializer):
    status = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=Subcategory.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all())

    class Meta:
        model = Logs
        fields = ['date', 'status', 'type', 'category', 'subcategory', 'amount', 'comment']
