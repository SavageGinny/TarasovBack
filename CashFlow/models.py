from django.db import models

class Category(models.Model):
    """Категория (например, Продукты, Транспорт)."""
    name: str = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'Category'
        app_label = 'CashFlow'
        managed = False


class Subcategory(models.Model):
    """Подкатегория, привязанная к категории (например, Магазин у дома)."""
    name: str = models.CharField(max_length=255, unique=True)
    category: Category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"

    class Meta:
        db_table = 'Subcategory'
        app_label = 'CashFlow'
        managed = False


class Status(models.Model):
    """Статус операции (например, Завершено, В ожидании)."""
    name: str = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'Status'
        app_label = 'CashFlow'
        managed = False


class Type(models.Model):
    """Тип операции (например, Доход, Расход)."""
    name: str = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'Type'
        app_label = 'CashFlow'
        managed = False


class Comments(models.Model):
    """Комментарий к записи."""
    content: str = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.content

    class Meta:
        db_table = 'Comments'
        app_label = 'CashFlow'
        managed = False


class Logs(models.Model):
    """Основная таблица записей ДДС."""
    date: models.DateField = models.DateField()
    status: Status = models.ForeignKey(Status, on_delete=models.CASCADE)
    type: Type = models.ForeignKey(Type, on_delete=models.CASCADE)
    category: Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory: Subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    amount: int = models.IntegerField()
    comment: Comments = models.ForeignKey(Comments, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.date} - {self.amount} ({self.category.name} / {self.subcategory.name})"

    class Meta:
        db_table = 'Log'
        app_label = 'CashFlow'
        managed = False
