import time
from functools import wraps
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import yfinance as yf
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ============ MOCK DATA (FALLBACK) ============
MOCK_DATA = {
    'AAPL': {
        'longName': 'Apple Inc.',
        'currentPrice': 185.50,
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'website': 'https://www.apple.com',
        'trailingPE': 28.5,
        'priceToBook': 45.2,
        'marketCap': 2900000000000,
        'volume': 52000000,
        'fiftyTwoWeekHigh': 199.62,
        'fiftyTwoWeekLow': 164.08,
        'fiftyDayAverage': 187.45,
        'twoHundredDayAverage': 181.32,
    },
    'TSLA': {
        'longName': 'Tesla Inc.',
        'currentPrice': 195.50,
        'sector': 'Consumer Discretionary',
        'industry': 'Vehicle Manufacturers',
        'website': 'https://www.tesla.com',
        'trailingPE': 65.2,
        'priceToBook': 15.8,
        'marketCap': 620000000000,
        'volume': 120000000,
        'fiftyTwoWeekHigh': 278.63,
        'fiftyTwoWeekLow': 138.80,
        'fiftyDayAverage': 216.45,
        'twoHundredDayAverage': 207.12,
    },
    'GOOGL': {
        'longName': 'Alphabet Inc.',
        'currentPrice': 139.50,
        'sector': 'Communication Services',
        'industry': 'Internet Software & Services',
        'website': 'https://www.google.com',
        'trailingPE': 22.5,
        'priceToBook': 5.8,
        'marketCap': 1850000000000,
        'volume': 18000000,
        'fiftyTwoWeekHigh': 198.08,
        'fiftyTwoWeekLow': 102.21,
        'fiftyDayAverage': 168.32,
        'twoHundredDayAverage': 155.67,
    }
}

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

# ============ HELPER FUNCTIONS ============
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

def get_stock_data(symbol):
    """Get stock data from yfinance or fallback to mock data"""
    symbol = symbol.upper().strip()
    
    try:
        # REMOVED timeout parameter - yfinance doesn't support it
        ticker = yf.Ticker(symbol)
        data = ticker.info
        
        if data and len(data) > 0:
            print(f"✓ Got real data for {symbol}")
            return data
    except Exception as e:
        print(f"yfinance error for {symbol}: {str(e)}")
    
    # Fallback to mock data
    if symbol in MOCK_DATA:
        print(f"⚠ Using fallback data for {symbol}")
        return MOCK_DATA[symbol]
    
    return None

def get_history_data(symbol, period='5d'):
    """Get history data from yfinance"""
    try:
        # REMOVED timeout parameter
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        return hist if not hist.empty else None
    except Exception as e:
        print(f"Error getting history for {symbol}: {str(e)}")
        return None

# ============ SERVE FRONTEND ============
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def status():
    return jsonify({"status": "ok", "cache_size": len(cache)})

# ============ STOCK ENDPOINT ============
@app.route('/api/stock/<symbol>')
def stock(symbol):
    try:
        cache_key = f"stock:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        
        if not symbol or len(symbol) > 10:
            return jsonify({"error": "Invalid symbol"}), 400
        
        info = get_stock_data(symbol)
        
        if not info:
            return jsonify({"error": f"Symbol '{symbol}' not found"}), 404
        
        # Try to get historical data for change calculation
        hist = get_history_data(symbol, '5d')
        
        current_price = info.get('currentPrice')
        if current_price is None and hist is not None and not hist.empty:
            current_price = float(hist['Close'].iloc[-1])
        elif current_price is None:
            current_price = 0
        else:
            current_price = float(current_price)
        
        change = 0
        pct = 0
        if hist is not None and not hist.empty and len(hist) > 1:
            prev_price = float(hist['Close'].iloc[-2])
            change = current_price - prev_price
            pct = (change / prev_price * 100) if prev_price > 0 else 0
        
        volume = info.get('volume', 0) or 0
        market_cap = info.get('marketCap', 'N/A')
        
        result = {
            "symbol": symbol,
            "name": safe_get(info, 'longName', symbol),
            "price": round(current_price, 2) if current_price else 0,
            "change": round(change, 2),
            "change_pct": round(pct, 2),
            "status": "up" if change >= 0 else "down",
            "volume": int(volume) if volume else 0,
            "marketcap": market_cap
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in stock endpoint: {str(e)}")
        return jsonify({"error": "Server error"}), 500

# ============ CHART ENDPOINT ============
@app.route('/api/chart/<symbol>')
def chart(symbol):
    try:
        cache_key = f"chart:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        hist = get_history_data(symbol, '5d')
        
        if hist is None or hist.empty:
            return jsonify({"error": "No data available"}), 404
        
        result = {
            "dates": [d.strftime("%m-%d") for d in hist.index],
            "closes": [round(float(x), 2) for x in hist['Close']]
        }
        
        set_cache(cache_key, result)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in chart endpoint: {str(e)}")
        return jsonify({"error": "Failed to fetch chart"}), 500

# ============ CHART EXTENDED ENDPOINT ============
@app.route('/api/chart-extended/<symbol>/<timeframe>')
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
        
        hist = get_history_data(symbol, timeframe)
        
        if hist is None or hist.empty:
            # Fallback to 1mo if period fails
            hist = get_history_data(symbol, '1mo')
            if hist is None or hist.empty:
                return jsonify({"error": "No data available"}), 404
        
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
        return jsonify({"error": "Failed to fetch chart"}), 500

# ============ METRICS ENDPOINT ============
@app.route('/api/metrics/<symbol>')
def metrics(symbol):
    try:
        cache_key = f"metrics:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        data = get_stock_data(symbol)
        
        if not data:
            return jsonify({"error": f"No data for '{symbol}'"}), 404
        
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
def info(symbol):
    try:
        cache_key = f"info:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        data = get_stock_data(symbol)
        
        if not data:
            return jsonify({"error": f"No data for '{symbol}'"}), 404
        
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
def financials(symbol):
    try:
        cache_key = f"financials:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        data = get_stock_data(symbol)
        
        if not data:
            return jsonify({"error": f"No data for '{symbol}'"}), 404
        
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
def valuation(symbol):
    try:
        cache_key = f"valuation:{symbol}"
        cached = get_cache(cache_key)
        if cached:
            return jsonify(cached)
        
        symbol = symbol.upper().strip()
        data = get_stock_data(symbol)
        
        if not data:
            return jsonify({"error": f"No data for '{symbol}'"}), 404
        
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

# ============ ERROR HANDLERS ============
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500

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
