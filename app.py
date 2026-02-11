import time
from functools import wraps
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import yfinance as yf
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ============ CACHE SYSTEM ============
cache = {}
CACHE_TTL = 300  # 5 minutes cache

def get_cache(key):
    """Get value from cache if not expired"""
    if key in cache:
        timestamp, value = cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        else:
            del cache[key]
    return None

def set_cache(key, value):
    """Set value in cache with timestamp"""
    cache[key] = (time.time(), value)

# ============ RATE LIMITING ============
request_times = {}

def rate_limit(max_requests=2, time_window=60):
    """Rate limit per endpoint"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            key = f"{func.__name__}:{client_ip}"
            now = time.time()
            
            if key not in request_times:
                request_times[key] = []
            
            # Clean old requests
            request_times[key] = [t for t in request_times[key] if now - t < time_window]
            
            if len(request_times[key]) >= max_requests:
                return jsonify({"error": "Rate limit exceeded. Please wait."}), 429
            
            request_times[key].append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def safe_get(data, key, default='N/A'):
    """Safely get value from dict"""
    try:
        value = data.get(key, default)
        if value is None or value == '':
            return default
        if isinstance(value, (int, float)):
            return round(value, 2) if isinstance(value, float) else value
        return str(value)
    except:
        return default

def safe_float(value, decimals=2):
    """Safely convert to float"""
    if value is None or value == 'N/A' or value == '':
        return 'N/A'
    try:
        return round(float(value), decimals)
    except:
        return 'N/A'

# ============ SERVE FRONTEND ============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "ok", "cache_size": len(cache)})

# ============ STOCK ENDPOINT ============
@app.route('/api/stock/<symbol>')
@rate_limit(max_requests=5, time_window=60)
def stock(symbol):
    try:
        cache_key = f"stock:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        
        # Validate symbol
        if not symbol or len(symbol) > 10:
            return jsonify({"error": "Invalid symbol"}), 400
        
        ticker = yf.Ticker(symbol)
        
        try:
            # Use shorter period first
            hist = ticker.history(period="5d")
            
            if hist.empty:
                return jsonify({"error": f"Symbol '{symbol}' not found or no data available"}), 404
            
            info = ticker.info
            
            if not info:
                return jsonify({"error": f"No data available for '{symbol}'"}), 404
            
            current_price = info.get('currentPrice')
            
            if current_price is None:
                current_price = float(hist['Close'].iloc[-1])
            else:
                try:
                    current_price = float(current_price)
                except:
                    current_price = float(hist['Close'].iloc[-1])
            
            prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else float(hist['Close'].iloc[-1])
            change = current_price - prev_price
            pct = (change / prev_price * 100) if prev_price > 0 else 0
            
            volume = info.get('volume', 0) or 0
            market_cap = info.get('marketCap', 'N/A')
            
            result = {
                "symbol": symbol,
                "name": safe_get(info, 'longName', symbol),
                "price": round(current_price, 2),
                "change": round(change, 2),
                "change_pct": round(pct, 2),
                "status": "up" if change >= 0 else "down",
                "volume": int(volume) if volume else 0,
                "marketcap": market_cap
            }
            
            set_cache(cache_key, result)
            return jsonify(result)
            
        except Exception as inner_error:
            print(f"Error fetching {symbol}: {str(inner_error)}")
            return jsonify({"error": f"Could not fetch data for '{symbol}'. Please try another symbol."}), 500
        
    except Exception as e:
        print(f"Error in stock endpoint: {str(e)}")
        return jsonify({"error": "Server error. Please try again."}), 500

# ============ CHART ENDPOINT ============
@app.route('/api/chart/<symbol>')
@rate_limit(max_requests=5, time_window=60)
def chart(symbol):
    try:
        cache_key = f"chart:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return jsonify({"error": "Not found"}), 404
        
        result = {
            "dates": [d.strftime("%m-%d") for d in hist.index],
            "closes": [round(float(x), 2) for x in hist['Close']]
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in chart endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch chart data"}), 500

# ============ CHART EXTENDED ENDPOINT ============
@app.route('/api/chart-extended/<symbol>/<timeframe>')
@rate_limit(max_requests=3, time_window=60)
def chart_extended(symbol, timeframe):
    try:
        cache_key = f"chart-extended:{symbol}:{timeframe}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        valid_timeframes = ['1mo', '3mo', '6mo', '1y', '5y', 'max']
        
        if timeframe not in valid_timeframes:
            timeframe = '1y'
        
        ticker = yf.Ticker(symbol)
        
        try:
            hist = ticker.history(period=timeframe)
        except:
            # Fallback to 1y if specified period fails
            hist = ticker.history(period='1y')
        
        if hist.empty:
            return jsonify({"error": "Not found"}), 404
        
        if timeframe in ['max', '5y']:
            dates = [d.strftime("%Y-%m-%d") for d in hist.index]
        elif timeframe == '1y':
            dates = [d.strftime("%m/%d") for d in hist.index]
        else:
            dates = [d.strftime("%m-%d") for d in hist.index]
        
        result = {
            "dates": dates,
            "closes": [round(float(x), 2) for x in hist['Close']],
            "volumes": [int(x) for x in hist['Volume']],
            "highs": [round(float(x), 2) for x in hist['High']],
            "lows": [round(float(x), 2) for x in hist['Low']],
            "timeframe": timeframe,
            "count": len(hist)
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in chart-extended endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch chart data"}), 500

# ============ METRICS ENDPOINT ============
@app.route('/api/metrics/<symbol>')
@rate_limit(max_requests=3, time_window=60)
def metrics(symbol):
    try:
        cache_key = f"metrics:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.info
        except:
            return jsonify({"error": f"Could not fetch metrics for '{symbol}'"}), 500
        
        if not data:
            return jsonify({"error": f"No data available for '{symbol}'"}), 404
        
        # Helper for percentage values
        def get_percentage(key):
            val = data.get(key)
            if val and val != 'N/A':
                try:
                    return round(float(val) * 100, 2)
                except:
                    return 'N/A'
            return 'N/A'
        
        result = {
            "symbol": symbol,
            "valuation": {
                "pe": safe_float(data.get('trailingPE'), 2),
                "pb": safe_float(data.get('priceToBook'), 2),
                "ps": safe_float(data.get('priceToSalesTrailing12Months'), 2),
                "eps": safe_float(data.get('trailingEps'), 4),
                "book_value": safe_float(data.get('bookValue'), 2),
            },
            "profitability": {
                "roe": get_percentage('returnOnEquity'),
                "roa": get_percentage('returnOnAssets'),
                "profit_margin": get_percentage('profitMargins'),
                "gross_margin": get_percentage('grossMargins'),
                "operating_margin": get_percentage('operatingMargins'),
            },
            "financial_health": {
                "der": safe_float(data.get('debtToEquity'), 2),
                "current_ratio": safe_float(data.get('currentRatio'), 2),
                "quick_ratio": safe_float(data.get('quickRatio'), 2),
                "total_debt": safe_get(data, 'totalDebt'),
                "total_equity": safe_get(data, 'totalEquity'),
            }
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in metrics endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch metrics"}), 500

# ============ INFO ENDPOINT ============
@app.route('/api/info/<symbol>')
@rate_limit(max_requests=3, time_window=60)
def info(symbol):
    try:
        cache_key = f"info:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.info
        except:
            return jsonify({"error": f"Could not fetch info for '{symbol}'"}), 500
        
        if not data:
            return jsonify({"error": f"No data available for '{symbol}'"}), 404
        
        ceo = 'N/A'
        try:
            officers = data.get('companyOfficers', [])
            if officers and len(officers) > 0:
                ceo = officers[0].get('name', 'N/A')
        except:
            pass
        
        result = {
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
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in info endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch info"}), 500

# ============ FINANCIALS ENDPOINT ============
@app.route('/api/financials/<symbol>')
@rate_limit(max_requests=3, time_window=60)
def financials(symbol):
    try:
        cache_key = f"financials:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.info
        except:
            return jsonify({"error": f"Could not fetch financials for '{symbol}'"}), 500
        
        if not data:
            return jsonify({"error": f"No data available for '{symbol}'"}), 404
        
        result = {
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
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in financials endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch financials"}), 500

# ============ VALUATION ENDPOINT ============
@app.route('/api/valuation/<symbol>')
@rate_limit(max_requests=3, time_window=60)
def valuation(symbol):
    try:
        cache_key = f"valuation:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        try:
            data = ticker.info
        except:
            return jsonify({"error": f"Could not fetch valuation for '{symbol}'"}), 500
        
        if not data:
            return jsonify({"error": f"No data available for '{symbol}'"}), 404
        
        result = {
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
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in valuation endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch valuation"}), 500

# ============ ERROR HANDLER ============
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Too many requests. Please wait before trying again."}), 429

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error. Please try again later."}), 500

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
