import time
from functools import wraps
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import traceback
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ============ RATE LIMITING ============
def rate_limit(calls_per_second=0.5):
    """Rate limiting decorator to prevent API throttling"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

def safe_get(data, key, default='N/A'):
    """Safely get value from dict and convert to proper format"""
    try:
        value = data.get(key, default)
        if value is None or value == '':
            return default
        if isinstance(value, (int, float)):
            if isinstance(value, float):
                return round(value, 2)
            return value
        if isinstance(value, str):
            return value
        if isinstance(value, (dict, list)):
            return default
        return str(value)
    except Exception as e:
        return default

def safe_float(value, decimals=2):
    """Safely convert value to float"""
    if value is None or value == 'N/A' or value == '':
        return 'N/A'
    try:
        result = float(value)
        return round(result, decimals)
    except (TypeError, ValueError):
        return 'N/A'

# ============ SERVE FRONTEND ============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "ok"})

@app.route('/api/stock/<symbol>')
@rate_limit(calls_per_second=0.5)
def stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="7d")
        
        if hist.empty:
            return jsonify({"error": "Not found"}), 404
        
        current_price = info.get('currentPrice')
        if current_price is None:
            current_price = float(hist['Close'].iloc[-1])
        else:
            current_price = float(current_price)
            
        prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else float(hist['Close'].iloc[-1])
        change = current_price - prev_price
        pct = (change / prev_price * 100) if prev_price > 0 else 0
        
        volume = info.get('volume', 0)
        if volume is None:
            volume = 0
        
        market_cap = info.get('marketCap', 'N/A')
        if market_cap is None:
            market_cap = 'N/A'
        
        return jsonify({
            "symbol": symbol,
            "name": safe_get(info, 'longName', symbol),
            "price": round(current_price, 2),
            "change": round(change, 2),
            "change_pct": round(pct, 2),
            "status": "up" if change >= 0 else "down",
            "volume": int(volume) if volume else 0,
            "marketcap": market_cap
        })
    except Exception as e:
        print(f"Error in stock endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart/<symbol>')
@rate_limit(calls_per_second=0.5)
def chart(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="7d")
        
        if hist.empty:
            return jsonify({"error": "Not found"}), 404
        
        dates = [d.strftime("%m-%d") for d in hist.index]
        closes = [round(float(x), 2) for x in hist['Close']]
        
        return jsonify({"dates": dates, "closes": closes})
    except Exception as e:
        print(f"Error in chart endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart-extended/<symbol>/<timeframe>')
@rate_limit(calls_per_second=0.5)
def chart_extended(symbol, timeframe):
    try:
        ticker = yf.Ticker(symbol)
        
        valid_timeframes = ['1mo', '3mo', '6mo', '1y', '5y', 'max']
        if timeframe not in valid_timeframes:
            timeframe = '1y'
        
        hist = ticker.history(period=timeframe)
        
        if hist.empty:
            return jsonify({"error": "Not found"}), 404
        
        if timeframe == 'max' or timeframe == '5y':
            dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        elif timeframe == '1y':
            dates = [d.strftime("%m/%d") for d in hist.index]
        else:
            dates = [d.strftime("%m-%d") for d in hist.index]
        
        closes = [round(float(x), 2) for x in hist['Close']]
        volumes = [int(x) for x in hist['Volume']]
        highs = [round(float(x), 2) for x in hist['High']]
        lows = [round(float(x), 2) for x in hist['Low']]
        
        return jsonify({
            "dates": dates,
            "closes": closes,
            "volumes": volumes,
            "highs": highs,
            "lows": lows,
            "timeframe": timeframe,
            "count": len(hist)
        })
    except Exception as e:
        print(f"Error in chart-extended endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics/<symbol>')
@rate_limit(calls_per_second=0.5)
def metrics(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        pe_ratio = safe_float(data.get('trailingPE'), 2)
        pb_ratio = safe_float(data.get('priceToBook'), 2)
        ps_ratio = safe_float(data.get('priceToSalesTrailing12Months'), 2)
        eps = safe_float(data.get('trailingEps'), 4)
        book_value = safe_float(data.get('bookValue'), 2)
        
        roe = data.get('returnOnEquity')
        if roe is not None and roe != 'N/A':
            try:
                roe = round(float(roe) * 100, 2)
            except:
                roe = 'N/A'
        else:
            roe = 'N/A'
            
        roa = data.get('returnOnAssets')
        if roa is not None and roa != 'N/A':
            try:
                roa = round(float(roa) * 100, 2)
            except:
                roa = 'N/A'
        else:
            roa = 'N/A'
            
        profit_margin = data.get('profitMargins')
        if profit_margin is not None and profit_margin != 'N/A':
            try:
                profit_margin = round(float(profit_margin) * 100, 2)
            except:
                profit_margin = 'N/A'
        else:
            profit_margin = 'N/A'
            
        gross_margin = data.get('grossMargins')
        if gross_margin is not None and gross_margin != 'N/A':
            try:
                gross_margin = round(float(gross_margin) * 100, 2)
            except:
                gross_margin = 'N/A'
        else:
            gross_margin = 'N/A'
            
        operating_margin = data.get('operatingMargins')
        if operating_margin is not None and operating_margin != 'N/A':
            try:
                operating_margin = round(float(operating_margin) * 100, 2)
            except:
                operating_margin = 'N/A'
        else:
            operating_margin = 'N/A'
        
        total_debt = safe_float(data.get('totalDebt'), 2)
        total_equity = safe_float(data.get('totalAssets'), 2)
        current_ratio = safe_float(data.get('currentRatio'), 2)
        quick_ratio = safe_float(data.get('quickRatio'), 2)
        
        der = 'N/A'
        if total_debt != 'N/A' and total_equity != 'N/A':
            try:
                if float(total_equity) > 0:
                    der = round(float(total_debt) / float(total_equity), 2)
            except:
                der = 'N/A'
        
        return jsonify({
            "symbol": symbol,
            "valuation": {
                "pe": pe_ratio,
                "pb": pb_ratio,
                "ps": ps_ratio,
                "eps": eps,
                "book_value": book_value,
            },
            "profitability": {
                "roe": roe,
                "roa": roa,
                "profit_margin": profit_margin,
                "gross_margin": gross_margin,
                "operating_margin": operating_margin,
            },
            "financial_health": {
                "der": der,
                "current_ratio": current_ratio,
                "quick_ratio": quick_ratio,
                "total_debt": total_debt,
                "total_equity": total_equity,
            }
        })
    except Exception as e:
        print(f"Error in metrics endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/info/<symbol>')
@rate_limit(calls_per_second=0.5)
def info(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        ceo = 'N/A'
        try:
            officers = data.get('companyOfficers', [])
            if officers and isinstance(officers, list) and len(officers) > 0:
                if isinstance(officers[0], dict) and 'name' in officers[0]:
                    ceo = officers[0]['name']
        except:
            ceo = 'N/A'
        
        return jsonify({
            "symbol": symbol,
            "name": safe_get(data, 'longName', symbol),
            "sector": safe_get(data, 'sector'),
            "industry": safe_get(data, 'industry'),
            "website": safe_get(data, 'website'),
            "description": safe_get(data, 'longBusinessSummary'),
            "current_price": safe_float(data.get('currentPrice'), 2),
            "52w_high": safe_float(data.get('fiftyTwoWeekHigh'), 2),
            "52w_low": safe_float(data.get('fiftyTwoWeekLow'), 2),
            "50d_avg": safe_float(data.get('fiftyDayAverage'), 2),
            "200d_avg": safe_float(data.get('twoHundredDayAverage'), 2),
            "dividend_rate": safe_float(data.get('trailingAnnualDividendRate'), 2),
            "dividend_yield": safe_float(data.get('dividendYield'), 4),
            "payout_ratio": safe_float(data.get('payoutRatio'), 4),
            "market_cap": safe_get(data, 'marketCap'),
            "shares_outstanding": safe_get(data, 'sharesOutstanding'),
            "shares_float": safe_get(data, 'floatShares'),
            "beta": safe_float(data.get('beta'), 2),
            "volume": safe_get(data, 'volume'),
            "avg_volume": safe_get(data, 'averageVolume'),
            "avg_volume_10d": safe_get(data, 'averageVolume10days'),
            "bid": safe_float(data.get('bid'), 2),
            "ask": safe_float(data.get('ask'), 2),
            "target_price": safe_float(data.get('targetPrice'), 2),
            "recommendation": safe_get(data, 'recommendationKey'),
            "number_of_analysts": safe_get(data, 'numberOfAnalystOpinions'),
            "ipo_date": safe_get(data, 'ipoDate'),
            "ceo": ceo,
            "trailing_pe": safe_float(data.get('trailingPE'), 2),
            "forward_pe": safe_float(data.get('forwardPE'), 2),
            "peg_ratio": safe_float(data.get('pegRatio'), 2),
        })
    except Exception as e:
        print(f"Error in info endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/financials/<symbol>')
@rate_limit(calls_per_second=0.5)
def financials(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        return jsonify({
            "symbol": symbol,
            "income_statement": {
                "total_revenue": safe_get(data, 'totalRevenue'),
                "revenue_growth": safe_float(data.get('revenueGrowth'), 2),
                "gross_profit": safe_get(data, 'grossProfit'),
                "operating_income": safe_get(data, 'operatingIncome'),
                "net_income": safe_get(data, 'netIncomeToCommon'),
                "earnings_growth": safe_float(data.get('earningsGrowth'), 2),
                "ebitda": safe_get(data, 'ebitda'),
            },
            "balance_sheet": {
                "total_assets": safe_get(data, 'totalAssets'),
                "total_liabilities": safe_get(data, 'totalLiabilities'),
                "total_equity": safe_get(data, 'totalEquity'),
                "total_debt": safe_get(data, 'totalDebt'),
                "cash": safe_get(data, 'totalCash'),
                "cash_per_share": safe_float(data.get('cashPerShare'), 2),
            },
            "cash_flow": {
                "operating_cash_flow": safe_get(data, 'operatingCashflow'),
                "free_cash_flow": safe_get(data, 'freeCashflow'),
                "capital_expenditure": safe_get(data, 'capitalExpenditures'),
            }
        })
    except Exception as e:
        print(f"Error in financials endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/valuation/<symbol>')
@rate_limit(calls_per_second=0.5)
def valuation(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        return jsonify({
            "symbol": symbol,
            "relative_valuation": {
                "trailing_pe": safe_float(data.get('trailingPE'), 2),
                "pe_ratio": safe_float(data.get('trailingPE'), 2),
                "forward_pe": safe_float(data.get('forwardPE'), 2),
                "pb_ratio": safe_float(data.get('priceToBook'), 2),
                "ps_ratio": safe_float(data.get('priceToSalesTrailing12Months'), 2),
                "peg_ratio": safe_float(data.get('pegRatio'), 2),
            },
            "dividend_metrics": {
                "dividend_rate": safe_float(data.get('trailingAnnualDividendRate'), 2),
                "dividend_yield": safe_float(data.get('dividendYield'), 4),
                "payout_ratio": safe_float(data.get('payoutRatio'), 4),
            },
            "risk_metrics": {
                "beta": safe_float(data.get('beta'), 2),
                "current_ratio": safe_float(data.get('currentRatio'), 2),
                "quick_ratio": safe_float(data.get('quickRatio'), 2),
            }
        })
    except Exception as e:
        print(f"Error in valuation endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("✅ GlobalStock Insight API")
    print("="*60)
    print("📍 Running at http://localhost:5000")
    print("\n📊 Available Endpoints:")
    print("  GET  /api/stock/<symbol>")
    print("  GET  /api/chart/<symbol>")
    print("  GET  /api/chart-extended/<symbol>/<timeframe>")
    print("  GET  /api/metrics/<symbol>")
    print("  GET  /api/info/<symbol>")
    print("  GET  /api/financials/<symbol>")
    print("  GET  /api/valuation/<symbol>")
    print("\n" + "="*60 + "\n")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)