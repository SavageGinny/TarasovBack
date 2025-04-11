"""
URL configuration for ITsolutionT project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CashFlow.API import *
from CashFlow.views import *

urlpatterns = [
    # Основные страницы
    path('', main_view, name='main'),
    path('add_log/', add_log_view, name='add_log'),
    path('update_references/', update_references_view, name='add_dictionary'),

    # API для получения подкатегорий
    path('get_subcategories/', get_subcategories, name='get_subcategories'),

    # API для добавления объекта
    path('api/add_object/', add_object, name='add_object'),

    # API для логов
    path('api/logs/', log_list, name='log_list'),
    path('api/logs/create/', log_create, name='log_create'),
    path('api/logs/<int:pk>/update/', log_update, name='log_update'),
    path('api/logs/<int:pk>/delete/', log_delete, name='log_delete'),

    # API для добавления статуса
    path('api/status/add/', add_status, name='add_status'),
    path('api/status/<int:pk>/update/', update_status, name='update_status'),
    path('api/status/<int:pk>/delete/', delete_status, name='delete_status'),

    # API для добавления типа
    path('api/type/add/', add_type, name='add_type'),
    path('api/type/<int:pk>/update/', update_type, name='update_type'),
    path('api/type/<int:pk>/delete/', delete_type, name='delete_type'),

    # API для добавления категории
    path('api/category/add/', add_category, name='add_category'),
    path('api/category/<int:pk>/update/', update_category, name='update_category'),
    path('api/category/<int:pk>/delete/', delete_category, name='delete_category'),

    # API для добавления подкатегории
    path('api/add_subcategory/', add_subcategory, name='add_subcategory'),
    path('api/subcategory/<int:pk>/update/', update_subcategory, name='update_subcategory'),
    path('api/subcategory/<int:pk>/delete/', delete_subcategory, name='delete_subcategory'),
]
