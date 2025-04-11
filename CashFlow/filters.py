from django_filters import rest_framework as filters
from .models import Log, Status, Type, Category, Subcategory

class LogFilter(filters.FilterSet):
    start_date = filters.ChoiceFilter(
        field_name="date",
        lookup_expr="gte",
        choices=lambda: [(date, date) for date in
                         Log.objects.values_list('date', flat=True).distinct().order_by('date')],
        label="",
        empty_label="Дата от"
    )
    end_date = filters.ChoiceFilter(
        field_name="date",
        lookup_expr="lte",
        choices=lambda: [(date, date) for date in
                         Log.objects.values_list('date', flat=True).distinct().order_by('date')],
        label="",
        empty_label="до"
    )

    status = filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        to_field_name='name',
        label='Статус',
    )

    type = filters.ModelChoiceFilter(
        queryset=Type.objects.all(),
        to_field_name='name',
        label='Тип',
    )

    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        to_field_name='name',
        label='Категория',
    )

    subcategory = filters.ModelChoiceFilter(
        queryset=Subcategory.objects.none(),
        to_field_name='name',
        label='Подкатегория',
    )

    class Meta:
        model = Log
        fields = ['start_date', 'end_date', 'status', 'type', 'category', 'subcategory']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        category = self.data.get("category")
        subcategory = self.data.get("subcategory")

        if category:
            try:
                category_obj = Category.objects.get(name=category)
                self.filters['subcategory'].queryset = Subcategory.objects.filter(category=category_obj)
            except Category.DoesNotExist:
                self.filters['subcategory'].queryset = Subcategory.objects.none()
        else:
            self.filters['subcategory'].queryset = Subcategory.objects.all()

        if subcategory and not category:
            try:
                subcategory_obj = Subcategory.objects.get(name=subcategory)
                self.filters['category'].queryset = Category.objects.filter(id=subcategory_obj.category.id)

                if hasattr(self, 'data') and self.data._mutable:
                    self.data['category'] = subcategory_obj.category.name
                elif hasattr(self, 'data'):
                    self.data = self.data.copy()
                    self.data['category'] = subcategory_obj.category.name

            except Subcategory.DoesNotExist:
                pass
