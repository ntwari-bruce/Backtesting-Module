import requests
from django.http import JsonResponse, HttpResponse
from .models import StockPrice, StockPrediction, BacktestResult
from datetime import datetime, timedelta
import logging
import pandas as pd
from decimal import Decimal
import joblib
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 




# Load the pre-trained model from the 'stocks/ML_model' directory
MODEL_PATH = 'stocks/ML_model/linear_regression_model.pkl'
model = joblib.load(MODEL_PATH)

def fetch_stock_data(request, symbol):
    try:
        api_key = 'QIYD959R52PO42RV'
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}'

        response = requests.get(url)
        if response.status_code != 200:
            return JsonResponse({'status': 'error', 'message': 'Failed to fetch data from Alpha Vantage'}, status=500)
        
        data = response.json()

        if "Error Message" in data or "Note" in data:
            # When API Lmit is reached  or symbol is invalid
            return JsonResponse({'status': 'error', 'message': data.get("Error Message", "API limit reached")}, status=500)

        time_series = data.get('Time Series (Daily)', {})
        
        # Two years ago from now
        two_years_ago = datetime.now() - timedelta(days=730)
        
        for date_str, price_date in time_series.items():
            date = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Only store date fro the last two years
            if date >= two_years_ago:
                StockPrice.objects.update_or_create(
                    symbol=symbol,
                    date=date,
                    defaults={
                        'open_price': price_date['1. open'],
                        'close_price': price_date['4. close'],
                        'high_price': price_date['2. high'],
                        'low_price': price_date['3. low'],
                        'volume': price_date['5. volume']
                    }
                )
        
        return JsonResponse({'status': 'success', 'message': 'Data fetched successfully'}, status=200)
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from Alpha Vantage: {e}")
        return JsonResponse({'status': 'error', 'message': 'Network error'}, status=500)
    except Exception as e:
        logging.error(f"An error occured: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occured'}, status=500)


def backtest_strategy(request):
    try:
        # Fetch the request parameters
        symbol = request.GET.get('symbol', None)
        try:
            initial_investment = Decimal(request.GET.get('initial_investment', 1000))  
        except InvalidOperation:
            return JsonResponse({'status': 'error', 'message': 'Invalid initial investment value'}, status=400)

        if not symbol:
            return JsonResponse({'status': 'error', 'message': 'Stock symbol is required'}, status=400)

        # Fetch stock price data from the database
        prices = StockPrice.objects.filter(symbol=symbol).order_by('date')

        if not prices.exists():
            return JsonResponse({'status': 'error', 'message': f'No historical data found for {symbol}'}, status=404)

        # Create a DataFrame from the StockPrice model data
        df = pd.DataFrame(list(prices.values('date', 'close_price')))
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Calculate 50-day and 20-day moving averages
        df['50_ma'] = df['close_price'].rolling(window=50).mean()
        df['20_ma'] = df['close_price'].rolling(window=20).mean()

        # Ensure there are no NaN values in the moving averages (e.g., at the beginning of the dataset)
        df['50_ma'].fillna(method='bfill', inplace=True)
        df['20_ma'].fillna(method='bfill', inplace=True)

        # Initialize backtesting variables
        cash = initial_investment  
        position = Decimal(0)  
        trades = 0
        max_drawdown = Decimal(0)
        peak_value = initial_investment

        # Loop through the historical prices
        for index, row in df.iterrows():
            try:
                close_price = Decimal(row['close_price'])
            except InvalidOperation:
                continue 

            try:
                # Handle invalid moving average values
                ma_50 = Decimal(row['50_ma'])
                ma_20 = Decimal(row['20_ma'])
            except InvalidOperation:
                continue
            # Calculate the current portfolio value (cash + value of stocks held)
            current_value = cash + position * close_price if position > 0 else cash

            # Update peak value to the maximum between the previous peak and current value
            peak_value = max(peak_value, current_value)

            # Calculate drawdown (the maximum loss from peak value)
            drawdown = (peak_value - current_value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)

            if close_price < ma_50 and position == 0:
                # Buy stock if price dips below the 50-day moving average
                position = cash / close_price  
                cash = Decimal(0)
                trades += 1
            elif close_price > ma_20 and position > 0:
                # Sell stock if price goes above the 20-day moving average
                cash = position * close_price  
                position = Decimal(0)
                trades += 1

        # Final portfolio value (cash + value of remaining stocks if any)
        final_value = cash + (position * df['close_price'].iloc[-1] if position > 0 else 0)

        # Calculate the return on investment (ROI)
        roi = (final_value - initial_investment) / initial_investment * 100

        # Round the results before storing them in the database
        rounded_final_value = round(final_value, 2)
        rounded_roi = round(roi, 2)
        rounded_max_drawdown = round(max_drawdown * 100, 2)

        # Store the results in the BacktestResult model
        BacktestResult.objects.create(
            symbol=symbol,
            initial_investment=initial_investment,
            final_value=rounded_final_value,
            roi=rounded_roi,
            max_drawdown=rounded_max_drawdown,
            trades_executed=trades
        )

        # Return the backtesting results
        result = {
            'initial_investment': initial_investment,
            'final_value': round(final_value, 2),
            'roi': round(roi, 2),
            'max_drawdown': round(max_drawdown * 100, 2),  
            'trades_executed': trades
        }

        return JsonResponse({'status': 'success', 'data': result}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def predict_stock_prices(request, symbol):
    try:
        # Fetch historical stock prices from the database
        prices = StockPrice.objects.filter(symbol=symbol).order_by('date')

        if not prices.exists():
            return JsonResponse({'status': 'error', 'message': f'No historical data found for {symbol}'}, status=404)

        # Prepare the data for prediction (e.g., using 'open_price', 'high_price', 'low_price', 'volume')
        X = np.array([[p.open_price, p.high_price, p.low_price, p.volume] for p in prices])

        # Generate a range of dates for the next 30 days
        last_date = prices.last().date
        prediction_dates = [last_date + timedelta(days=i) for i in range(1, 31)]

        # Use the pre-trained model to predict the next 30 days of prices
        predicted_prices = model.predict(X[-30:])

        # Store predictions in the database (update if the record already exists)
        for i, date in enumerate(prediction_dates):
            predicted_price = Decimal(predicted_prices[i])
            StockPrediction.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={'predicted_price': predicted_price}
            )

        # Return the predicted prices as a JSON response (rounding to 2 decimal places)
        prediction_data = [{'date': str(date), 'predicted_price': str(round(pred, 2))} for date, pred in zip(prediction_dates, predicted_prices)]
        return JsonResponse({'status': 'success', 'predictions': prediction_data}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def generate_report(request, symbol):
    try:
        # Fetch historical stock prices and predictions
        historical_prices = StockPrice.objects.filter(symbol=symbol).order_by('date')
        predicted_prices = StockPrediction.objects.filter(symbol=symbol).order_by('date')

        if not historical_prices.exists() or not predicted_prices.exists():
            return JsonResponse({'status': 'error', 'message': 'No data found for the report'}, status=404)

        # Prepare actual historical prices
        actual_dates = [p.date for p in historical_prices]
        actual_prices = [p.close_price for p in historical_prices]

        # Prepare predicted prices for the next 30 days
        prediction_dates = [p.date for p in predicted_prices]
        predicted_prices_list = [p.predicted_price for p in predicted_prices]

        # Fetch the backtest results from the database
        backtest_results = BacktestResult.objects.filter(symbol=symbol).last()

        if not backtest_results:
            return JsonResponse({'status': 'error', 'message': 'No backtest results found'}, status=404)

        # Visualization using Matplotlib (comparison between historical and future predictions)
        plt.figure(figsize=(10, 6))
        plt.plot(actual_dates, actual_prices, label='Actual Prices (Historical)')
        plt.plot(prediction_dates, predicted_prices_list, label='Predicted Prices (Next 30 Days)', linestyle='--')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title(f'Stock Price Prediction Report for {symbol}')
        plt.legend()

        # Save the plot to a PDF
        buffer = BytesIO()
        plt.savefig(buffer, format='pdf')
        buffer.seek(0)

        # Check if the request wants a PDF download
        if 'pdf' in request.GET:
            return HttpResponse(buffer, content_type='application/pdf')

        # Return key metrics and prediction data in JSON format
        prediction_data = [{'date': str(date), 'predicted_price': round(pred, 2)} for date, pred in zip(prediction_dates, predicted_prices_list)]
        return JsonResponse({
            'status': 'success',
            'backtest_metrics': {
                'initial_investment': backtest_results.initial_investment,
                'final_value': backtest_results.final_value,
                'roi': backtest_results.roi,
                'max_drawdown': backtest_results.max_drawdown,
                'trades_executed': backtest_results.trades_executed
            },
            'predictions': prediction_data
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
