from .models import StockData
import pandas as pd
from decimal import Decimal

def backtest_strategy(symbol, initial_investment, short_window, long_window):
    data = StockData.objects.filter(symbol=symbol).order_by('date')
    df = pd.DataFrame(list(data.values()))

    # Convert Decimal fields to float
    decimal_columns = ['open_price', 'high_price', 'low_price', 'close_price']
    for col in decimal_columns:
        df[col] = df[col].astype(float)

    df['short_ma'] = df['close_price'].rolling(window=short_window).mean()
    df['long_ma'] = df['close_price'].rolling(window=long_window).mean()

    df['position'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'position'] = 1
    df.loc[df['short_ma'] < df['long_ma'], 'position'] = -1

    df['returns'] = df['close_price'].pct_change()
    df['strategy_returns'] = df['position'].shift(1) * df['returns']

    total_return = (1 + df['strategy_returns']).prod() - 1
    max_drawdown = (df['strategy_returns'].cumsum() - df['strategy_returns'].cumsum().cummax()).min()
    num_trades = (df['position'].diff() != 0).sum()

    return {
        'total_return': float(total_return),
        'max_drawdown': float(max_drawdown),
        'num_trades': int(num_trades),
        'final_value': float(initial_investment * (1 + total_return))
    }