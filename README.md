# Charity Crowdfunding Transaction System

This is a first working prototype of a Crowdfunding Transaction System. Specific assumptions have been made around access patterns and acceptable latency goals for each of the API calls.

## Features

- Store donation transactions with multiple currencies
- Parse donation amount strings with currency symbols (e.g., "$10", "£15", "€4")
- Currency conversion with exchange rates and fees
- Reporting APIs for charity performance and donor statistics
- Lightweight implementation with minimal external dependencies

## API Endpoints

The system provides the following API endpoints:

1. `get_highest_grossing_charity_over_24_hours()`: Returns the highest grossing charity over the last 24 hours with its last 5 transactions
2. `get_running_totals_for_all_charities()`: Returns the running total for all charities in EUR and the global total
3. `get_most_generous_donator()`: Returns the most generous donator and their total donation amount in EUR

## Design

The system follows object-oriented design principles with clear separation of concerns:

- **Models**:
  - `ExchangeRate`: Represents currency exchange rates with fee handling
  - `Donation`: Parses donation strings and stores donation information
  - `Charity`: Tracks donations for a specific charity
  - `Donator`: Tracks donations from a specific donor

- **Services**:
  - `ExchangeRateService`: Manages exchange rates and currency conversion
  - `DonationService`: Processes donations and handles reporting

- **API Layer**:
  - `Api`: Provides a clean interface for system functionality

## Performance Considerations

The system is optimized for donation processing, with `add_donation` operations running in O(1) time. The design prioritizes write performance, which is critical for a donation platform that may experience spikes in donation volume.

The reporting endpoint `get_highest_charity_over_24_hours` runs in O(n) time, where n is the number of donations in the system. This design choice prioritizes write performance over read performance, which is appropriate for the expected usage pattern where donations are frequent and reporting is infrequent.

### Potential Optimizations for Read Performance

If reporting frequency increases substantially, potential optimizations include:

1. **Time-Window Caching**: Implement a caching mechanism for 24-hour window calculations that invalidates only when new donations fall within the cached window.

2. **Indexed/Ordered Data Structures**: Maintain time-indexed or ordered data structures to reduce the cost of time-range queries.

3. **Sliding Window Tracking**: Track donations in a sliding window data structure that efficiently handles newest/oldest donation transitions.

4. **Materialized Views**: For database implementations, we can use materialized views that periodically refresh aggregation data. Even a simpler regular view can help us in speeding up frequent queries.

## Assumptions

1. **Currencies**: The system ONLY handles USD, GBP, and EUR currencies with symbols ($, £, €).

2. **Exchange Rates**: 
   - When a direct exchange rate is not available for a specific date, the system uses the closest available date.
   - If a direct conversion path isn't available, the system attempts conversion via intermediate currencies (e.g., USD→GBP→EUR).

3. **Floating Point Precision**: The system uses native `float` types for monetary values rather than `Decimal` to minimize external dependencies. In a production system, `Decimal` would be preferred for accuracy.

4. **Currency Conversion**: When converting between currencies, the fee is applied first, then the exchange rate.

5. **Timezones** :

- Input timestamps may include ONLY EST, CET, or GMT timezone information
- All timestamps are converted to UTC for storage and processing
- Timezone conversion uses fixed offsets (EST: UTC-5, CET: UTC+1, GMT: UTC)
- No daylight saving time adjustments are made for simplicity

6. **Data Persistence**: This prototype uses in-memory storage; a production system would use a database.

7. **API Format**: The API returns structured data that can be converted to JSON.

8. **24-hour Window**: The "last 24 hours" is calculated based on the requested reference time.

## Setup and Running

1. Clone the repository
2. Ensure Python 3.x is installed
3. Place `exchange_rates.csv` and `donations.csv` in the same directory as the script. Make sure they use the format mentioned below.
4. Run the main script: `python main.py`

### Run tests

We have installed `pytest` for the tests (added in `test` subfolder).

```
python3 -m venv venv
source venv/bin/activate
(venv) > pip install pytest
(venv) > pytest
```

## CSV File Formats

#### Exchange Rates CSV

```csv
source,target,rate,fee,date
GBP,USD,1.26,0.5,20 Jan 2023
...
```

#### Donations CSV

```csv
donator,amount,charity,timestamp
User1,$10,Cancer Research,21 Jan 2023 10:15 EST
...
```

## Future Improvements

1. **Precision Improvements**: Replace `float` with `Decimal` to avoid floating-point precision issues with monetary values.

2. **Structured Logging**: Replace print statements with proper logging infrastructure.

3. **Read Performance**: Implement caching strategies for high-volume reporting scenarios.

4. **Currency Support**: Expand support for additional currencies and more sophisticated conversion paths (BFS/DFS).

5. **Database Integration**: On a production system, add persistence layer with appropriate indexing.
