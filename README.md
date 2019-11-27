# python_dfis
Python package to help implement a demand forecastability inventory strategy.

## Expected Preprocessing
1. Slice for date range (scope).
2. sku, brand, channel, origin_id, dest_id, date, quantity
3. Levels config: .csv of column combinations where index is level depth or number (id). Additionally two columns; one for period_type ('W'='weekly') and one for n_periods.
