# stock_data/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('fetch/', views.fetch_data, name='fetch_data'),
    path('backtest/', views.run_backtest, name='run_backtest'),
    path('predict/', views.get_predictions, name='get_predictions'),
    path('report/', views.get_report, name='get_report'),
]
