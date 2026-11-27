from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [

    path(
        'register/',
        views.register_view,
        name='register'
    ),

    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    path(
    'dashboard/',
    views.dashboard_view,
    name='dashboard'
),
    path(
    'transactions/',
    views.transaction_list,
    name='transaction_list'
),

path(
    'transactions/add/',
    views.add_transaction,
    name='add_transaction'
),

path(
    'transactions/edit/<int:pk>/',
    views.edit_transaction,
    name='edit_transaction'
),

path(
    'transactions/delete/<int:pk>/',
    views.delete_transaction,
    name='delete_transaction'
),

path(
    'monthly-report/',
    views.monthly_report,
    name='monthly_report'
),

path(
    'add-budget/',
    views.add_budget,
    name='add_budget'
),

path(
    'budget-dashboard/',
    views.budget_dashboard,
    name='budget_dashboard'
),

]