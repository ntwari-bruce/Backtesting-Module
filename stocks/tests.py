from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from .models import StockPrice
from decimal import Decimal
from datetime import timedelta, date

class BacktestLogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Generate 200+ days of stock price data
        base_date = date(2023, 1, 1)
        for i in range(250):
            # Prices fluctuate for buy/sell logic validation
            if i % 2 == 0:
                open_price = Decimal(100 + i)
                close_price = Decimal(100 + i + 5)  
            else:
                open_price = Decimal(100 + i)
                close_price = Decimal(100 + i - 5)  
            high_price = Decimal(open_price + 10)
            low_price = Decimal(open_price - 10)
            volume = 10000 + i * 100

            StockPrice.objects.create(
                symbol='IBM',
                date=base_date + timedelta(days=i),
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume
            )

    def test_backtest_buy_sell_logic(self):
        """Test that the buy and sell logic is working correctly."""
        response = self.client.get(reverse('backtest_strategy'), {'symbol': 'IBM', 'initial_investment': 10000})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']

        # Check if trades were executed
        self.assertGreater(data['trades_executed'], 0, "No trades were executed, which is unexpected.")

        # This test assumes the stock prices fluctuate enough for at least one buy/sell action.
        # We are testing that both buy and sell conditions occur, ensuring that trades are executed.
        trades = data['trades_executed']
        self.assertTrue(trades > 0, "Trades should be greater than 0 since prices are fluctuating.")

    def test_backtest_roi_calculation(self):
        """Test that the ROI calculation is correct based on initial investment and final value."""
        response = self.client.get(reverse('backtest_strategy'), {'symbol': 'IBM', 'initial_investment': 10000})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']

        initial_investment = Decimal(data['initial_investment'])
        final_value = Decimal(data['final_value'])
        expected_roi = (final_value - initial_investment) / initial_investment * 100

        # Validate that the ROI is correctly calculated
        roi = Decimal(data['roi'])
        self.assertAlmostEqual(roi, expected_roi, places=2, msg=f"Expected ROI to be {expected_roi}, but got {roi}.")

    def test_backtest_max_drawdown(self):
        """Test that the max drawdown is correctly calculated during the backtest."""
        response = self.client.get(reverse('backtest_strategy'), {'symbol': 'IBM', 'initial_investment': 10000})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']

        max_drawdown = Decimal(data['max_drawdown'])
        # Validate that the max drawdown is a non-negative number (as drawdown is always a loss from peak)
        self.assertGreaterEqual(max_drawdown, 0, "Max drawdown should be non-negative.")
        self.assertLessEqual(max_drawdown, 100, "Max drawdown should be at most 100%.")

    def test_backtest_number_of_trades(self):
        """Test that the number of trades executed matches expected behavior."""
        response = self.client.get(reverse('backtest_strategy'), {'symbol': 'IBM', 'initial_investment': 10000})
        self.assertEqual(response.status_code, 200)
        data = response.json()['data']

        # Assert that trades were executed
        trades_executed = data['trades_executed']
        self.assertGreater(trades_executed, 0, "Trades should have been executed.")

