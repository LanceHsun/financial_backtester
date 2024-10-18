from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import fetch_stock_data
from .backtesting import backtest_strategy
from .reports import generate_report
from .ml_model import predict_stock_prices, train_and_save_model
import traceback
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
def fetch_data(request):
    symbol = request.GET.get('symbol', 'AAPL')
    try:
        fetch_stock_data(symbol)
        return JsonResponse({"message": f"Data fetched for {symbol}"})
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def run_backtest(request):
    symbol = request.GET.get('symbol', 'AAPL')
    initial_investment = float(request.GET.get('initial_investment', 10000))
    short_window = int(request.GET.get('short_window', 50))
    long_window = int(request.GET.get('long_window', 200))
    
    try:
        results = backtest_strategy(symbol, initial_investment, short_window, long_window)
        return JsonResponse(results)
    except Exception as e:
        logger.error(f"Error running backtest for {symbol}: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_predictions(request):
    symbol = request.GET.get('symbol', 'AAPL')
    days = int(request.GET.get('days', 30))
    
    try:
        logger.info(f"Fetching predictions for {symbol} for {days} days")
        predictions = predict_stock_prices(symbol, days)
        logger.info(f"Successfully generated predictions for {symbol}")
        return JsonResponse({"predictions": predictions})
    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logger.error(f"Error in get_predictions for {symbol}: {error_message}\n{stack_trace}")
        return JsonResponse({
            "error": error_message,
            "stack_trace": stack_trace
        }, status=500)

@require_http_methods(["GET"])
def get_report(request):
    symbol = request.GET.get('symbol', 'AAPL')
    initial_investment = float(request.GET.get('initial_investment', 10000))
    short_window = int(request.GET.get('short_window', 50))
    long_window = int(request.GET.get('long_window', 200))
    
    try:
        return generate_report(symbol, initial_investment, short_window, long_window)
    except Exception as e:
        logger.error(f"Error generating report for {symbol}: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)