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

@api_view(['GET'])
@permission_classes([AllowAny])
def log_list(request: HttpRequest) -> Response:
    """
    Возвращает список логов с возможностью фильтрации по различным параметрам.
    """
    logs = Logs.objects.using('DDS').select_related('status', 'type', 'category', 'subcategory', 'comment')

    status = request.GET.get('status')
    if status:
        logs = logs.filter(status__name=status)

    type_name = request.GET.get('type')
    if type_name:
        logs = logs.filter(type__name=type_name)

    category = request.GET.get('category')
    if category:
        logs = logs.filter(category__name=category)

    subcategory = request.GET.get('subcategory')
    if subcategory:
        logs = logs.filter(subcategory__name=subcategory)

    start_date = request.GET.get('start_date')
    if start_date:
        logs = logs.filter(date__gte=start_date)

    end_date = request.GET.get('end_date')
    if end_date:
        logs = logs.filter(date__lte=end_date)

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
def log_create(request: HttpRequest) -> Response:
    """
    Создание новой записи с привязкой комментариев и подкатегорий, используя имена объектов.
    """
    category_name = request.data.get('category')
    subcategory_name = request.data.get('subcategory')
    status_name = request.data.get('status')
    type_name = request.data.get('type')
    amount = request.data.get('amount')
    comment_text = request.data.get('comment')
    date = request.data.get('date')

    logger.debug(f"Received data: {request.data}")

    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        logger.error(f"Category '{category_name}' not found")
        return Response({"error": f"Category '{category_name}' not found"}, status=401)

    try:
        subcategory = Subcategory.objects.get(id=subcategory_name)
    except Subcategory.DoesNotExist:
        logger.error(f"Subcategory '{subcategory_name}' not found")
        return Response({"error": f"Subcategory '{subcategory_name}' not found"}, status=402)

    try:
        status = Status.objects.get(name=status_name)
    except Status.DoesNotExist:
        logger.error(f"Status '{status_name}' not found")
        return Response({"error": f"Status '{status_name}' not found"}, status=403)

    try:
        type = Type.objects.get(name=type_name)
    except Type.DoesNotExist:
        logger.error(f"Type '{type_name}' not found")
        return Response({"error": f"Type '{type_name}' not found"}, status=405)

    comment_id = None
    if comment_text:
        try:
            comment_instance = Comments.objects.get(content=comment_text)
            comment_id = comment_instance.id
        except Comments.DoesNotExist:
            new_comment = Comments.objects.create(content=comment_text)
            comment_id = new_comment.id
            logger.debug(f"Created new comment with ID: {comment_id}")

    log_data = {
        "date": date,
        "status": status.id,
        "type": type.id,
        "category": category.id,
        "subcategory": subcategory.id,
        "amount": amount,
        "comment": comment_id
    }

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
def log_update(request: HttpRequest, pk: int) -> Response:
    """
    Обновление записи лога по его ID с возможностью изменения всех параметров.
    """
    try:
        log = Logs.objects.get(pk=pk)
    except Logs.DoesNotExist:
        logger.error(f"Log with ID '{pk}' not found")
        return Response({"error": f"Log with ID '{pk}' not found"}, status=404)

    category_name = request.data.get('category', log.category.name)
    subcategory_name = request.data.get('subcategory', log.subcategory.name)
    status_name = request.data.get('status', log.status.name)
    type_name = request.data.get('type', log.type.name)
    amount = request.data.get('amount', log.amount)
    comment_text = request.data.get('comment', log.comment.content)
    date = request.data.get('date', log.date)

    logger.debug(f"Received data for update: {request.data}")

    try:
        category = Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        logger.error(f"Category '{category_name}' not found")
        return Response({"error": f"Category '{category_name}' not found"}, status=401)

    try:
        subcategory = Subcategory.objects.get(id=subcategory_name)
    except Subcategory.DoesNotExist:
        logger.error(f"Subcategory '{subcategory_name}' not found")
        return Response({"error": f"Subcategory '{subcategory_name}' not found"}, status=402)

    try:
        status = Status.objects.get(name=status_name)
    except Status.DoesNotExist:
        logger.error(f"Status '{status_name}' not found")
        return Response({"error": f"Status '{status_name}' not found"}, status=403)

    try:
        type = Type.objects.get(name=type_name)
    except Type.DoesNotExist:
        logger.error(f"Type '{type_name}' not found")
        return Response({"error": f"Type '{type_name}' not found"}, status=405)

    comment_id = None
    if comment_text:
        try:
            comment_instance = Comments.objects.get(content=comment_text)
            comment_id = comment_instance.id
        except Comments.DoesNotExist:
            new_comment = Comments.objects.create(content=comment_text)
            comment_id = new_comment.id
            logger.debug(f"Created new comment with ID: {comment_id}")

    log_data = {
        "date": date,
        "status": status.id,
        "type": type.id,
        "category": category.id,
        "subcategory": subcategory.id,
        "amount": amount,
        "comment": comment_id
    }

    serializer = PostLogSerializer(log, data=log_data)
    if serializer.is_valid():
        with transaction.atomic():
            serializer.save()
        logger.debug(f"Log entry with ID {pk} updated successfully")
        return Response(serializer.data, status=200)

    logger.error(f"Validation error: {serializer.errors}")
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def log_delete(request: HttpRequest, pk: int) -> Response:
    """
    Удаляет лог по его ID.
    """
    log = get_object_or_404(Logs, pk=pk)
    log.delete()
    return Response({'message': 'Deleted successfully'}, status=204)

@api_view(['POST'])
def add_status(request: HttpRequest) -> Response:
    """
    Добавляет новый статус.
    """
    serializer = StatusSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_type(request: HttpRequest) -> Response:
    """
    Добавляет новый тип.
    """
    serializer = TypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_category(request: HttpRequest) -> Response:
    """
    Добавляет новую категорию.
    """
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_subcategory(request: HttpRequest) -> Response:
    """
    Добавляет новую подкатегорию.
    """
    serializer = SubcategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_status(request: HttpRequest, pk: int) -> Response:
    """
    Обновление существующего статуса по его ID.
    """
    try:
        status = Status.objects.get(pk=pk)
    except Status.DoesNotExist:
        return Response({"error": f"Status with ID '{pk}' not found"}, status=404)

    serializer = StatusSerializer(status, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_type(request: HttpRequest, pk: int) -> Response:
    """
    Обновление существующего типа по его ID.
    """
    try:
        type = Type.objects.get(pk=pk)
    except Type.DoesNotExist:
        return Response({"error": f"Type with ID '{pk}' not found"}, status=404)

    serializer = TypeSerializer(type, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_category(request: HttpRequest, pk: int) -> Response:
    """
    Обновление существующей категории по её ID.
    """
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error": f"Category with ID '{pk}' not found"}, status=404)

    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_subcategory(request: HttpRequest, pk: int) -> Response:
    """
    Обновление существующей подкатегории по её ID.
    """
    try:
        subcategory = Subcategory.objects.get(pk=pk)
    except Subcategory.DoesNotExist:
        return Response({"error": f"Subcategory with ID '{pk}' not found"}, status=404)

    serializer = SubcategorySerializer(subcategory, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_status(request: HttpRequest, pk: int) -> Response:
    """
    Удаляет статус по его ID.
    """
    status_instance = get_object_or_404(Status, pk=pk)
    status_instance.delete()
    return Response({'message': 'Status deleted successfully'}, status=204)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_type(request: HttpRequest, pk: int) -> Response:
    """
    Удаляет тип по его ID.
    """
    type_instance = get_object_or_404(Type, pk=pk)
    type_instance.delete()
    return Response({'message': 'Type deleted successfully'}, status=204)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_category(request: HttpRequest, pk: int) -> Response:
    """
    Удаляет категорию по её ID.
    """
    category_instance = get_object_or_404(Category, pk=pk)
    category_instance.delete()
    return Response({'message': 'Category deleted successfully'}, status=204)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_subcategory(request: HttpRequest, pk: int) -> Response:
    """
    Удаляет подкатегорию по её ID.
    """
    subcategory_instance = get_object_or_404(Subcategory, pk=pk)
    subcategory_instance.delete()
    return Response({'message': 'Subcategory deleted successfully'}, status=204)


@api_view(['POST'])
def add_object(request: HttpRequest) -> Response:
    """
    Добавляет объект одного из следующих типов: статус, тип, категория, подкатегория.
    """
    object_type = request.data.get('object_type')

    if object_type == 'status':
        serializer = StatusSerializer(data=request.data)
    elif object_type == 'type':
        serializer = TypeSerializer(data=request.data)
    elif object_type == 'category':
        serializer = CategorySerializer(data=request.data)
    elif object_type == 'subcategory':
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
