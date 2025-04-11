import csv
import logging
import requests
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import *

from .serializers import *

logger = logging.getLogger(__name__)
# ==== LOG ====

@api_view(['GET'])
@permission_classes([AllowAny])
def log_list(request):
    logs = Logs.objects.using('DDS').select_related('status', 'type', 'category', 'subcategory', 'comment')

    # Фильтрация по статусу
    status = request.GET.get('status')
    if status:
        logs = logs.filter(status__name=status)

    # Фильтрация по типу
    type_name = request.GET.get('type')
    if type_name:
        logs = logs.filter(type__name=type_name)

    # Фильтрация по категории
    category = request.GET.get('category')
    if category:
        logs = logs.filter(category__name=category)

    # Фильтрация по подкатегории
    subcategory = request.GET.get('subcategory')
    if subcategory:
        logs = logs.filter(subcategory__name=subcategory)

    # Фильтрация по дате
    start_date = request.GET.get('start_date')
    if start_date:
        logs = logs.filter(date__gte=start_date)

    end_date = request.GET.get('end_date')
    if end_date:
        logs = logs.filter(date__lte=end_date)

    # Формирование данных
    data = [
        {
            "date": log.date,
            "status": log.status.name,
            "type": log.type.name,
            "category": log.category.name,
            "subcategory": log.subcategory.name,
            "amount": log.amount,
            "comment": log.comment.content
        }
        for log in logs
    ]

    return Response(data)

@api_view(['POST'])
@permission_classes([AllowAny])
def log_create(request):
    """
    Создание новой записи с привязкой комментариев и подкатегорий, используя имена объектов.
    """
    category_name = request.data.get('category')
    subcategory_name = request.data.get('subcategory')
    status_name = request.data.get('status')
    type_name = request.data.get('type')
    amount = request.data.get('amount')
    comment_text = request.data.get('comment')  # Получаем текст комментария
    date = request.data.get('date')

    logger.debug(f"Received data: {request.data}")  # Логируем входящие данные

    # Проверка существования объектов по имени
    try:
        # Поиск объектов по имени
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        logger.error(f"Category '{category_name}' not found")  # Логируем ошибку
        return Response({"error": f"Category '{category_name}' not found"}, status=401)

    try:
        subcategory = Subcategory.objects.get(id=subcategory_name)
    except Subcategory.DoesNotExist:
        logger.error(f"Subcategory '{subcategory_name}' not found")  # Логируем ошибку
        return Response({"error": f"Subcategory '{subcategory_name}' not found"}, status=402)

    try:
        status = Status.objects.get(name=status_name)
    except Status.DoesNotExist:
        logger.error(f"Status '{status_name}' not found")  # Логируем ошибку
        return Response({"error": f"Status '{status_name}' not found"}, status=403)

    try:
        type = Type.objects.get(name=type_name)
    except Type.DoesNotExist:
        logger.error(f"Type '{type_name}' not found")  # Логируем ошибку
        return Response({"error": f"Type '{type_name}' not found"}, status=405)

    # Если комментарий передан, проверяем его наличие или создаём новый
    comment_id = None
    if comment_text:
        try:
            # Если комментарий существует, получаем его
            comment_instance = Comments.objects.get(content=comment_text)
            comment_id = comment_instance.id
        except Comments.DoesNotExist:
            # Если комментария нет, создаём новый
            new_comment = Comments.objects.create(content=comment_text)
            comment_id = new_comment.id
            logger.debug(f"Created new comment with ID: {comment_id}")  # Логируем создание нового комментария

    # Подготовка данных для создания новой записи
    log_data = {
        "date": date,
        "status": status.id,
        "type": type.id,
        "category": category.id,
        "subcategory": subcategory.id,
        "amount": amount,
        "comment": comment_id  #
    }

    # Сериализация и сохранение записи
    serializer = PostLogSerializer(data=log_data)
    if serializer.is_valid():
        with transaction.atomic():
            serializer.save()
        logger.debug("Log entry saved successfully")
        return Response(serializer.data, status=201)

    logger.error(f"Validation error: {serializer.errors}")
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([AllowAny])
def log_update(request, pk):
    log = get_object_or_404(Logs, pk=pk)
    serializer = LogSerializer(log, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def log_delete(request, pk):
    log = get_object_or_404(Logs, pk=pk)
    log.delete()
    return Response({'message': 'Deleted successfully'}, status=204)


@api_view(['POST'])
def add_status(request):
    if request.method == 'POST':
        serializer = StatusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_type(request):
    if request.method == 'POST':
        serializer = TypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_category(request):
    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_subcategory(request):
    print(request.data)
    if request.method == 'POST':
        serializer = SubcategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_object(request):
    object_type = request.data.get('object_type')

    if object_type == 'status':
        serializer = StatusSerializer(data=request.data)
    elif object_type == 'type':
        serializer = TypeSerializer(data=request.data)
    elif object_type == 'category':
        serializer = CategorySerializer(data=request.data)
    elif object_type == 'subcategory':
        # Проверяем, что категория передана
        category_name = request.data.get('category')
        if not category_name:
            return Response({"error": "Category is required for subcategory"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        request.data['category'] = category.id
        serializer = SubcategorySerializer(data=request.data)
    else:
        return Response({"error": "Invalid object type"}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)