from django.shortcuts import render
from datetime import datetime
import yfinance as yf
import pandas as pd

def stock_table(request):
    tickers = ['AAPL', 'MSFT', 'TSLA']
    stock_data = []

    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")

            # 計算 RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            latest_rsi = round(rsi.iloc[-1], 2) if not rsi.empty else 'N/A'

            #配息日格式轉換
            timestamp = stock.info.get('exDividendDate', None)

            if timestamp:
                ex_div_date = datetime.fromtimestamp(timestamp).date()  # 轉成 YYYY-MM-DD 格式
            else:
                ex_div_date = 'N/A'

            stock_data.append({
                'symbol': symbol,
                'close': round(hist.tail(1)['Close'][0],2),
                'volume': stock.info.get('volume', 'N/A'),#int(stock.info['volume']),
                'dividend': stock.info.get('lastDividendValue', 'N/A'),#stock.info['lastDividendValue'],
                'dividend_date': ex_div_date,#stock.info['exDividendDate'],
                'rsi': latest_rsi
            })
        except Exception as e:
            stock_data.append({
                'symbol': symbol,
                'error': str(e)
            })

    return render(request, 'stocks/index.html', {'stocks': stock_data})
