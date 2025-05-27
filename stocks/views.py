from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
import yfinance as yf
import pandas as pd
import json
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

    # 計算布林通道（20日平均線 + 上下2個標準差）
    hist['bb_middle'] = hist['Close'].rolling(window=20).mean()
    hist['bb_std'] = hist['Close'].rolling(window=20).std()
    hist['bb_upper'] = hist['bb_middle'] + 2 * hist['bb_std']
    hist['bb_lower'] = hist['bb_middle'] - 2 * hist['bb_std']

    # RSI 計算 (14日)
    delta = hist['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    hist['rsi'] = 100 - (100 / (1 + rs))

    # MACD 計算 (12, 26, 9)
    ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
    ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
    hist['macd'] = ema12 - ema26
    hist['signal'] = hist['macd'].ewm(span=9, adjust=False).mean()
    hist['histogram'] = hist['macd'] - hist['signal']


    chart_data = []
    for i in range(len(hist)):
        row = hist.iloc[i]
        chart_data.append({
            'date': row.name.strftime('%Y-%m-%d'),
            'open': round(row['Open'], 2),
            'close': round(row['Close'], 2),
            'high': round(row['High'], 2),
            'low': round(row['Low'], 2),
            'volume': int(row['Volume']) if not pd.isna(row['Volume']) else 0,
            'bb_upper': round(row['bb_upper'], 2) if not pd.isna(row['bb_upper']) else None,
            'bb_middle': round(row['bb_middle'], 2) if not pd.isna(row['bb_middle']) else None,
            'bb_lower': round(row['bb_lower'], 2) if not pd.isna(row['bb_lower']) else None,
            'date': row.name.strftime('%Y-%m-%d'),
            'rsi': round(row['rsi'], 2) if not pd.isna(row['rsi']) else None,
            'macd': round(row['macd'], 2) if not pd.isna(row['macd']) else None,
            'signal': round(row['signal'], 2) if not pd.isna(row['signal']) else None,
            'histogram': round(row['histogram'], 2) if not pd.isna(row['histogram']) else None,
        })

    context = {
        'symbol': symbol,
        'chart_data': json.dumps(chart_data)
    }

    return render(request, 'stocks/detail.html', context)
