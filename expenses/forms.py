from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, Category
from .models import Budget

class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction

        fields = [
            'category',
            'transaction_type',
            'amount',
            'description',
            'date'
        ]

        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'description': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(
            user=user
        )

    def clean(self):
        cleaned_data = super().clean()

        category = cleaned_data.get('category')
        transaction_type = cleaned_data.get('transaction_type')

        if category and transaction_type:
            if category.category_type != transaction_type:
                raise forms.ValidationError(
                    "Please select a category matching the transaction type."
                )

        return cleaned_data

class BudgetForm(forms.ModelForm):

    class Meta:

        model = Budget

        fields = [
            'category',
            'month',
            'amount'
        ]

        widgets = {

            'month': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'amount': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter budget amount',
                    'min': '0.01',
                    'step': '0.01'
                }
            )

        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(
            user=user,
            category_type='expense'
        )