from django.db import models
from django.contrib.auth.models import User


# 1. Category Model
class Category(models.Model):

    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    category_type = models.CharField(
        max_length=10,
        choices=CATEGORY_TYPES
    )

    def __str__(self):
        return self.name


# 2. Transaction Model
class Transaction(models.Model):

    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT
    )

    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


# 3. Budget Model
class Budget(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    month = models.DateField()

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        unique_together = ('user', 'category', 'month')

    def __str__(self):

        return f"{self.user.username} - {self.category.name} - {self.month}"