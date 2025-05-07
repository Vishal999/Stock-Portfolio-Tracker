from flask import Flask, render_template, request, jsonify
import yfinance as yf
from datetime import datetime
import json

app = Flask(__name__)

# Load portfolio from JSON file
def load_portfolio():
    try:
        with open('portfolio.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save portfolio to JSON file
def save_portfolio(portfolio):
    with open('portfolio.json', 'w') as f:
        json.dump(portfolio, f)

@app.route('/')
def index():
    return render_template('index.html', portfolio=load_portfolio())

@app.route('/add_stock', methods=['POST'])
def add_stock():
    data = request.json
    symbol = data['symbol']
    shares = float(data['shares'])
    
    try:
        stock = yf.Ticker(symbol)
        current_price = stock.info['regularMarketPrice']
        
        portfolio = load_portfolio()
        portfolio.append({
            'symbol': symbol,
            'shares': shares,
            'purchase_price': current_price,
            'purchase_date': datetime.now().strftime('%Y-%m-%d')
        })
        save_portfolio(portfolio)
        
        return jsonify({'success': True})
    except:
        return jsonify({'success': False, 'error': 'Invalid stock symbol'})

@app.route('/remove_stock', methods=['POST'])
def remove_stock():
    data = request.json
    symbol = data['symbol']
    
    portfolio = load_portfolio()
    portfolio = [stock for stock in portfolio if stock['symbol'] != symbol]
    save_portfolio(portfolio)
    
    return jsonify({'success': True})

@app.route('/get_portfolio_data')
def get_portfolio_data():
    portfolio = load_portfolio()
    updated_portfolio = []
    
    for stock in portfolio:
        ticker = yf.Ticker(stock['symbol'])
        current_price = ticker.info['regularMarketPrice']
        
        profit_loss = (current_price - stock['purchase_price']) * stock['shares']
        profit_loss_percentage = ((current_price - stock['purchase_price']) / stock['purchase_price']) * 100
        
        stock_data = {
            **stock,
            'current_price': current_price,
            'profit_loss': round(profit_loss, 2),
            'profit_loss_percentage': round(profit_loss_percentage, 2)
        }
        updated_portfolio.append(stock_data)
    
    return jsonify(updated_portfolio)

if __name__ == '__main__':
    app.run(debug=True)
