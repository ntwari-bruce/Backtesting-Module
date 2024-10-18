from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'date')
        ordering = ['-date']


class StockPrediction(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('symbol', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.symbol} - {self.date}: {self.predicted_price}"

class BacktestResult(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField(auto_now_add=True)  # Date of the backtest execution
    initial_investment = models.DecimalField(max_digits=15, decimal_places=2)
    final_value = models.DecimalField(max_digits=15, decimal_places=2)
    roi = models.DecimalField(max_digits=5, decimal_places=2)
    max_drawdown = models.DecimalField(max_digits=5, decimal_places=2)
    trades_executed = models.IntegerField()

    def __str__(self):
        return f"Backtest for {self.symbol} on {self.date}"