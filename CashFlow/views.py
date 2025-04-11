from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages

from .forms import *
from .models import *

import requests


def get_subcategories(request):
    category_name = request.GET.get('category_name')

    if category_name:
        # Найдем категорию по имени
        try:
            category = Category.objects.get(name=category_name)
            subcategories = Subcategory.objects.filter(category=category)

            # Формируем список подкатегорий
            subcategory_data = [{'id': subcategory.id, 'name': subcategory.name} for subcategory in subcategories]

            return JsonResponse({'subcategories': subcategory_data})
        except Category.DoesNotExist:
            return JsonResponse({'subcategories': []}, status=400)
    else:
        return JsonResponse({'subcategories': []}, status=400)
def main_view(request):
    """
    Главная страница — отображение формы фильтрации и данных через API.
    """
    form = FilterLogsForm(request.GET or None)

    # Параметры фильтра передаются в API-запрос
    params = {}
    if form.is_valid():
        cleaned = form.cleaned_data
        if cleaned.get("status"):
            params['status'] = cleaned['status']
        if cleaned.get("type"):
            params['type'] = cleaned['type']
        if cleaned.get("category"):
            params['category'] = cleaned['category']
        if cleaned.get("subcategory"):
            params['subcategory'] = cleaned['subcategory']
        if cleaned.get("start_date"):
            params['start_date'] = cleaned['start_date']
        if cleaned.get("end_date"):
            params['end_date'] = cleaned['end_date']

    # Запрос к API
    from urllib.parse import urlencode
    import requests

    query_string = urlencode(params)
    api_url = f"http://localhost:8000/api/logs/?{query_string}"
    response = requests.get(api_url)
    logs_data = response.json() if response.status_code == 200 else []

    return render(request, "index.html", {"form": form, "logs": logs_data})


def add_log_view(request):
    """
    Страница добавления записи — отображение формы для добавления записи через API.
    """
    form = CreateLogForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Собираем данные из формы
            form_data = form.cleaned_data

            # Формируем параметры для API-запроса
            data = {
                'status': form_data['status'],
                'type': form_data['type'],
                'category': form_data['category'],
                'subcategory': form_data['subcategory'],
                'amount': form_data['amount'],
                'comment': form_data['comment'],
                'date': form_data['date'],
            }

            # Запрос к API для добавления записи
            api_url = "http://localhost:8000/api/logs/"
            response = requests.post(api_url, data=data)

            if response.status_code == 201:  # Если запись добавлена успешно
                return redirect('main')  # Перенаправление на главную страницу
            else:
                form.add_error(None, "Ошибка при добавлении записи.")

    return render(request, 'add_log.html', {'form': form})

def update_references_view(request):
    if request.method == 'POST':
        form = AddObjectForm(request.POST)
        if form.is_valid():
            # Получаем тип объекта из формы
            object_type = form.cleaned_data['object_type']
            name = form.cleaned_data['name']
            category = form.cleaned_data.get('category', None)

            # Добавляем объект в нужный справочник
            if object_type == 'status':
                Status.objects.create(name=name)
                messages.success(request, 'Статус успешно добавлен!')
            elif object_type == 'type':
                Type.objects.create(name=name)
                messages.success(request, 'Тип успешно добавлен!')
            elif object_type == 'category':
                Category.objects.create(name=name)
                messages.success(request, 'Категория успешно добавлена!')
            elif object_type == 'subcategory':
                if category:
                    category_obj = Category.objects.get(id=category)
                    Subcategory.objects.create(name=name, category=category_obj)
                    messages.success(request, 'Подкатегория успешно добавлена!')
                else:
                    messages.error(request, 'Необходимо выбрать категорию для подкатегории!')

            return redirect('main')  # Перенаправление на главную страницу после успешного добавления
    else:
        form = AddObjectForm()

    return render(request, 'add_object.html', {'form': form})




