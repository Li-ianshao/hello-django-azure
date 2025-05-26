from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import yfinance as yf
import pandas as pd

def stock_table(request):
    tickers = ['AAPL', 'MSFT', 'TSLA', 'KO', 'T', 'NFLX', 'MCD', 'PEP', 'XOM', 'WMT', 'JNJ', 'NVDA', 'META']
    stock_data = []

    for symbol in tickers:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")

            # 收盤價
            close = round(hist["Close"][-1],2) if not hist.empty else 'N/A'

            # RSI 計算（14日）
            delta = hist["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean().iloc[-1]
            avg_loss = loss.rolling(window=14).mean().iloc[-1]
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = round(100 - (100 / (1 + rs)), 2) if avg_gain and avg_loss else 'N/A'

            # 當日漲跌幅 %
            try:
                price_change = round(((hist["Close"][-1] - hist["Close"][-2]) / hist["Close"][-2]) * 100, 2)
            except:
                price_change = 'N/A'

            # volume delta
            try:
                volume = stock.info.get("volume", 0)
                avg_volume = stock.info.get("averageVolume", 0)
                volume_delta = round((volume/avg_volume)*100,2)
            except:
                volume_delta = 'N/A'

            # 配息日
            ex_div_ts = stock.info.get("exDividendDate", None)
            ex_div_date = datetime.fromtimestamp(ex_div_ts).strftime('%Y-%m-%d') if ex_div_ts else 'N/A'

            # 每股配息
            dividend = stock.info.get("lastDividendValue", 'N/A')

            # 此次配息率 = 配息 ÷ 收盤價
            try:
                dividend_ratio = round(float(dividend) / float(close) * 100, 2)
            except:
                dividend_ratio = 'N/A'

            # 殖利率（年度總配息 ÷ 價格）
            dividend_yield = stock.info.get("dividendYield", 0)#round(stock.info.get("dividendYield", 0) * 100, 2) if stock.info.get("dividendYield") else 'N/A'


            stock_data.append({
                "symbol": symbol,
                "close": close,
                "ex_dividend_date": ex_div_date,
                "dividend": dividend,
                "dividend_ratio": dividend_ratio,
                "yield": dividend_yield,
                "price_change": price_change,
                "year_low": stock.info.get("fiftyTwoWeekLow", 'N/A'),
                "year_high": stock.info.get("fiftyTwoWeekHigh", 'N/A'),
                "rsi": rsi,
                "volume_delta": volume_delta,
            })
        except Exception as e:
            stock_data.append({
                'symbol': symbol,
                'error': str(e)
            })

   
    return render(request, 'stocks/index.html', {'stocks': stock_data})
    
def stock_detail(request, symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period='3mo')

    chart_data = hist[['Close']].reset_index()
    chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
    chart_json = chart_data.to_json(orient='records')

    context = {
        'symbol': symbol,
        'chart_data': chart_json,
    }
    return render(request, 'stocks/detail.html', context)
