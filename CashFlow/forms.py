from django import forms
from django_select2.forms import Select2Widget
from .models import *


class FilterLogsForm(forms.Form):
    status = forms.ChoiceField(
        label="Статус",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите статус'})
    )

    type = forms.ChoiceField(
        label="Тип",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите тип'})
    )

    category = forms.ChoiceField(
        label="Категория",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите категорию'})
    )

    subcategory = forms.ChoiceField(
        label="Подкатегория",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите подкатегорию'})
    )

    start_date = forms.DateField(
        label="Дата начала",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    end_date = forms.DateField(
        label="Дата конца",
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['status'].choices = self.get_status_choices()
        self.fields['type'].choices = self.get_type_choices()
        self.fields['category'].choices = self.get_category_choices()

        # Если категория уже выбрана, то сразу фильтруем подкатегории
        category_name = None
        if 'category' in self.data and self.data.get('category'):
            category_name = self.data.get('category')

        self.fields['subcategory'].choices = self.get_subcategory_choices(category_name)

    @staticmethod
    def get_status_choices():
        statuses = Status.objects.all()
        return [("", "--- Выберите статус ---")] + [(s.name, s.name) for s in statuses]

    @staticmethod
    def get_type_choices():
        types = Type.objects.all()
        return [("", "--- Выберите тип ---")] + [(t.name, t.name) for t in types]

    @staticmethod
    def get_category_choices():
        categories = Category.objects.all()
        return [("", "--- Выберите категорию ---")] + [(c.name, c.name) for c in categories]

    @staticmethod
    def get_subcategory_choices(category_name=None):
        """
        Получение списка подкатегорий по имени категории (если передано).
        """
        if not category_name:
            subcategories = Subcategory.objects.all()
        else:
            try:
                category = Category.objects.get(name=category_name)
                subcategories = Subcategory.objects.filter(category_id=category.id)
            except Category.DoesNotExist:
                subcategories = Subcategory.objects.none()

        return [("", "--- Выберите подкатегорию ---")] + [(s.name, s.name) for s in subcategories]


class CreateLogForm(forms.Form):
    status = forms.ChoiceField(
        label="Статус",
        choices=[],
        required=True,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите статус'})
    )

    type = forms.ChoiceField(
        label="Тип",
        choices=[],
        required=True,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите тип'})
    )

    category = forms.ChoiceField(
        label="Категория",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите категорию'})
    )

    subcategory = forms.ChoiceField(
        label="Подкатегория",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите подкатегорию'})
    )

    amount = forms.FloatField(
        label="Сумма",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    comment = forms.ChoiceField(
        label="Комментарий",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите комментарий'})
    )

    date = forms.DateField(
        label="Дата",
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Заполнение выборок для статусов, типов, категорий и подкатегорий
        self.fields['status'].choices = self.get_status_choices()
        self.fields['type'].choices = self.get_type_choices()
        self.fields['category'].choices = self.get_category_choices()
        category_name = None
        if 'category' in self.data and self.data.get('category'):
            category_name = self.data.get('category')

        self.fields['subcategory'].choices = self.get_subcategory_choices(category_name)

        self.fields['comment'].choices = self.get_comment_choices()

    @staticmethod
    def get_status_choices():
        statuses = Status.objects.all()
        return [("", "--- Выберите статус ---")] + [(s.name, s.name) for s in statuses]

    @staticmethod
    def get_type_choices():
        types = Type.objects.all()
        return [("", "--- Выберите тип ---")] + [(t.name, t.name) for t in types]

    @staticmethod
    def get_category_choices():
        categories = Category.objects.all()
        return [("", "--- Выберите категорию ---")] + [(c.name, c.name) for c in categories]

    @staticmethod
    def get_subcategory_choices(category_name=None):
        """
        Получение списка подкатегорий по имени категории (если передано).
        """
        if not category_name:
            subcategories = Subcategory.objects.all()
        else:
            try:
                category = Category.objects.get(name=category_name)
                subcategories = Subcategory.objects.filter(category_id=category.id)
            except Category.DoesNotExist:
                subcategories = Subcategory.objects.none()

        return [("", "--- Выберите подкатегорию ---")] + [(s.name, s.name) for s in subcategories]

    @staticmethod
    def get_comment_choices():
        # Получаем список комментариев для выбора
        comments = Comments.objects.all()
        return [("", "--- Выберите комментарий ---")] + [(c.id, c.content) for c in comments]


from django import forms
from .models import Status, Type, Category, Subcategory
from django_select2.forms import Select2Widget


class AddObjectForm(forms.Form):
    OBJECT_TYPE_CHOICES = [
        ('status', 'Статус'),
        ('type', 'Тип'),
        ('category', 'Категория'),
        ('subcategory', 'Подкатегория'),
    ]

    object_type = forms.ChoiceField(
        label="Тип объекта",
        choices=OBJECT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    name = forms.CharField(
        label="Название",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    category = forms.ChoiceField(
        label="Категория",
        choices=[],
        required=False,
        widget=Select2Widget(attrs={'class': 'form-select', 'data-placeholder': 'Выберите категорию'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Подгружаем категории в поле category
        self.fields['category'].choices = self.get_category_choices()

    @staticmethod
    def get_category_choices():
        categories = Category.objects.all()
        return [("", "--- Выберите категорию ---")] + [(c.id, c.name) for c in categories]