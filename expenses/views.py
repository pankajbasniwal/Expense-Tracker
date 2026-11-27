from .forms import RegisterForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Transaction
from .forms import TransactionForm
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
from .models import Budget, Category
from .forms import BudgetForm
from datetime import date
import json
from django.db.models.functions import TruncMonth
from django.http import request

@login_required
def dashboard_view(request):

    user = request.user

    # Get total income
    total_income = Transaction.objects.filter(
        user=user,
        transaction_type='income'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')


    # Get total expenses
    total_expenses = Transaction.objects.filter(
        user=user,
        transaction_type='expense'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')


    # Calculate balance
    balance = total_income - total_expenses


    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=user
    ).order_by('-date', '-created_at')[:5]

     # Category-wise expense data
    
    category_expenses = Transaction.objects.filter(
            user=request.user,
            transaction_type='expense'
        ).values(
            'category__name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')
    
    
    category_labels = [
            item['category__name']
            for item in category_expenses
        ]
    
    category_values = [
            float(item['total'])
            for item in category_expenses
        ]

    
    
        # Income and expense chart data
    
    income_expense_data = [
            float(total_income),
            float(total_expenses)
        ]



    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'category_labels': json.dumps(category_labels),

        'category_values': json.dumps(category_values),

        'income_expense_data': json.dumps(income_expense_data),
        'monthly_labels': json.dumps(monthly_labels),

        'monthly_income': json.dumps(monthly_income),

        'monthly_expenses': json.dumps(monthly_expenses),
    }



    
   
    return render(
        request,
        'dashboard.html',
        context
    )

# Monthly Income and Expense Comparison

today = timezone.localdate()

# Generate the last 6 months
month_starts = []

for offset in range(5, -1, -1):

    total_month = today.year * 12 + today.month - 1 - offset

    year = total_month // 12
    month = total_month % 12 + 1

    month_starts.append(date(year, month, 1))


# First day of the next month
if today.month == 12:
    next_month_start = date(today.year + 1, 1, 1)
else:
    next_month_start = date(today.year, today.month + 1, 1)


monthly_transactions = Transaction.objects.filter(
    user=request.user,
    date__gte=month_starts[0],
    date__lt=next_month_start,
    transaction_type__in=['income', 'expense']
).annotate(
    month=TruncMonth('date')
).values(
    'month',
    'transaction_type'
).annotate(
    total=Sum('amount')
)


# Prepare chart data

monthly_data = {}

for month_start in month_starts:

    key = month_start.strftime('%Y-%m')

    monthly_data[key] = {
        'income': 0,
        'expense': 0
    }


for item in monthly_transactions:

    key = item['month'].strftime('%Y-%m')

    monthly_data[key][item['transaction_type']] = float(
        item['total'] or 0
    )


monthly_labels = [
    month.strftime('%b %Y')
    for month in month_starts
]

monthly_income = [
    monthly_data[month.strftime('%Y-%m')]['income']
    for month in month_starts
]

monthly_expenses = [
    monthly_data[month.strftime('%Y-%m')]['expense']
    for month in month_starts
]

def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('login')

    else:

        form = RegisterForm()

    return render(
        request,
        'register.html',
        {'form': form}
    )

@login_required
def add_transaction(request):

    if request.method == 'POST':

        form = TransactionForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            transaction = form.save(commit=False)

            transaction.user = request.user

            transaction.save()

            messages.success(
                request,
                "Transaction added successfully!"
            )

            return redirect('transaction_list')

    else:

        form = TransactionForm(user=request.user)

    return render(
        request,
        'add_transaction.html',
        {'form': form}
    )

@login_required
def transaction_list(request):

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-date', '-created_at')

    return render(
        request,
        'transaction_list.html',
        {'transactions': transactions}
    )

@login_required
def edit_transaction(request, pk):

    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':

        form = TransactionForm(
            request.POST,
            instance=transaction,
            user=request.user
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Transaction updated successfully!"
            )

            return redirect('transaction_list')

    else:

        form = TransactionForm(
            instance=transaction,
            user=request.user
        )

    return render(
        request,
        'edit_transaction.html',
        {'form': form}
    )

@login_required
def delete_transaction(request, pk):

    transaction = get_object_or_404(
        Transaction,
        pk=pk,
        user=request.user
    )

    if request.method == 'POST':

        transaction.delete()

        messages.success(
            request,
            "Transaction deleted successfully!"
        )

        return redirect('transaction_list')

    return redirect('transaction_list')

@login_required
def monthly_report(request):

    selected_month = request.GET.get(
        'month',
        timezone.localdate().strftime('%Y-%m')
    )

    # Validate selected month
    try:
        report_date = datetime.strptime(
            selected_month,
            '%Y-%m'
        )

    except ValueError:
        report_date = timezone.localdate()
        selected_month = report_date.strftime('%Y-%m')


    # Get monthly transactions
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=report_date.year,
        date__month=report_date.month
    ).order_by('-date', '-created_at')


    # Calculate monthly income
    monthly_income = transactions.filter(
        transaction_type='income'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')


    # Calculate monthly expenses
    monthly_expenses = transactions.filter(
        transaction_type='expense'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')


    # Calculate monthly balance
    monthly_balance = monthly_income - monthly_expenses


    # Category-wise expense calculation
    category_expenses = transactions.filter(
        transaction_type='expense'
    ).values(
        'category__name'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')


    # Prepare chart labels
    category_labels = [
        item['category__name']
        for item in category_expenses
    ]


    # Prepare chart amounts
    category_amounts = [
        float(item['total'])
        for item in category_expenses
    ]


    # Prepare bar chart data
    chart_income = float(monthly_income)

    chart_expenses = float(monthly_expenses)


    # Context dictionary
    context = {

        'transactions': transactions,

        'monthly_income': monthly_income,

        'monthly_expenses': monthly_expenses,

        'monthly_balance': monthly_balance,

        'selected_month': selected_month,

        'category_labels': category_labels,

        'category_amounts': category_amounts,

        'chart_income': chart_income,

        'chart_expenses': chart_expenses,

    }


    return render(
        request,
        'monthly_report.html',
        context
    )

@login_required
def add_budget(request):

    if request.method == 'POST':

        form = BudgetForm(
            request.POST,
            user=request.user
        )

        if form.is_valid():

            budget = form.save(commit=False)

            budget.user = request.user

            # Store the first day of the selected month
            budget.month = date(
                budget.month.year,
                budget.month.month,
                1
            )

            try:

                budget.save()

                messages.success(
                    request,
                    "Budget created successfully!"
                )

                return redirect('budget_dashboard')

            except IntegrityError:

                messages.error(
                    request,
                    "A budget already exists for this category and month."
                )

    else:

        form = BudgetForm(user=request.user)

    return render(
        request,
        'add_budget.html',
        {'form': form}
    )

@login_required
def budget_dashboard(request):

    selected_month = request.GET.get(
        'month',
        date.today().strftime('%Y-%m')
    )

    try:

        report_date = date.fromisoformat(
            selected_month + '-01'
        )

    except ValueError:

        report_date = date.today().replace(day=1)

        selected_month = report_date.strftime('%Y-%m')


    budgets = Budget.objects.filter(
        user=request.user,
        month=report_date
    ).select_related('category')


    budget_data = []

    for budget in budgets:

        spent = Transaction.objects.filter(
            user=request.user,
            category=budget.category,
            transaction_type='expense',
            date__year=report_date.year,
            date__month=report_date.month
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')


        percentage = float(
            spent / budget.amount * 100
        )

        remaining = budget.amount - spent

        if percentage >= 100:
            status = 'exceeded'

        elif percentage >= 80:
            status = 'warning'

        else:
            status = 'safe'


        budget_data.append({

            'category': budget.category.name,

            'limit': budget.amount,

            'spent': spent,

            'remaining': remaining,

            'percentage': percentage,

            'status': status

        })


    context = {

        'budget_data': budget_data,

        'selected_month': selected_month,

    }

    return render(
        request,
        'budget_dashboard.html',
        context
    )