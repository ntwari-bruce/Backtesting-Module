"""
URL configuration for financial_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from stocks.views import fetch_stock_data
from stocks.views import backtest_strategy, predict_stock_prices, generate_report

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fetch-stock/<str:symbol>/', fetch_stock_data, name='fetch_stock'),
    path('backtest/', backtest_strategy, name='backtest_strategy'),
    path('predict-stock/<str:symbol>/', predict_stock_prices, name='predict_stock'),
    path('generate-report/<str:symbol>/', generate_report, name='generate_report'),
]
