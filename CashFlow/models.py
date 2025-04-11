from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'Category'
        app_label = 'CashFlow'
        managed = False


class Subcategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Subcategory'
        app_label = 'CashFlow'
        managed = False



class Status(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'Status'
        app_label = 'CashFlow'
        managed = False


class Type(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'Type'
        app_label = 'CashFlow'
        managed = False


class Comments(models.Model):
    content = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'Comments'
        app_label = 'CashFlow'
        managed = False



class Logs(models.Model):
    date = models.DateField()
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    amount = models.IntegerField()
    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Log'
        app_label = 'CashFlow'
        managed = False
