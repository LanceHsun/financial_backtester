import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import io
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from .models import StockData
from .backtesting import backtest_strategy
from .ml_model import predict_stock_prices
import pandas as pd

def generate_report(symbol, initial_investment, short_window, long_window):
    # Fetch data
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    
    if not data:
        raise ValueError(f"No data found for symbol {symbol}")
    
    # Convert to DataFrame
    df = pd.DataFrame(list(data.values()))
    
    # Perform backtesting
    backtest_results = backtest_strategy(symbol, initial_investment, short_window, long_window)
    
    # Get predictions
    predictions = predict_stock_prices(symbol)
    
    # Ensure we have the correct number of dates for predictions
    prediction_dates = df['date'].tail(len(predictions))
    
    # Create plots
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['close_price'], label='Actual')
    plt.plot(prediction_dates, predictions, label='Predicted')
    plt.legend()
    plt.title(f'{symbol} Stock Price - Actual vs Predicted')
    plt.xlabel('Date')
    plt.ylabel('Price')
    
    # Save plot to buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()  # 清理图形
    
    # Generate PDF report
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'
    
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, f"Report for {symbol}")
    p.drawString(100, 730, f"Backtest Results:")
    p.drawString(120, 710, f"Total Return: {backtest_results['total_return']:.2%}")
    p.drawString(120, 690, f"Max Drawdown: {backtest_results['max_drawdown']:.2%}")
    p.drawString(120, 670, f"Number of Trades: {backtest_results['num_trades']}")
    p.drawString(120, 650, f"Final Value: ${backtest_results['final_value']:.2f}")
    
    # Use ImageReader to handle the BytesIO object
    img = ImageReader(buffer)
    p.drawImage(img, 100, 300, width=400, height=200)
    
    p.showPage()
    p.save()
    
    return response