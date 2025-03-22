import pytest
from datetime import datetime
from models import ExchangeRate
from exchange_rate_service import ExchangeRateService

@pytest.fixture
def exchange_rate_service():
    """Create an exchange rate service with some test data"""
    service = ExchangeRateService()
    
    # Add some exchange rates
    service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.22, 0.5, datetime(2023, 1, 21)))
    service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.18, 0.3, datetime(2023, 1, 21)))
    service.add_exchange_rate(ExchangeRate("USD", "EUR", 0.92, 0.4, datetime(2023, 1, 21)))
    
    return service

def test_add_exchange_rate():
    """Test adding an exchange rate to the service"""
    service = ExchangeRateService()
    rate = ExchangeRate("GBP", "USD", 1.22, 0.5, datetime(2023, 1, 21))
    service.add_exchange_rate(rate)
    
    # Check that the rate was added
    date_str = "2023-01-21"
    source_target = "GBP_USD"
    assert date_str in service.exchange_rates
    assert source_target in service.exchange_rates[date_str]
    assert service.exchange_rates[date_str][source_target] == rate

def test_get_exchange_rate_direct(exchange_rate_service):
    """Test getting a direct exchange rate"""
    rate = exchange_rate_service.get_exchange_rate("GBP", "USD", datetime(2023, 1, 21))
    assert rate is not None
    assert rate.source == "GBP"
    assert rate.target == "USD"
    assert rate.rate == 1.22
    assert rate.fee == 0.5
    assert rate.date == datetime(2023, 1, 21)

def test_get_exchange_rate_same_currency(exchange_rate_service):
    """Test getting an exchange rate for the same currency (should return 1.0 with no fee)"""
    rate = exchange_rate_service.get_exchange_rate("USD", "USD", datetime(2023, 1, 21))
    assert rate is not None
    assert rate.source == "USD"
    assert rate.target == "USD"
    assert rate.rate == 1.0
    assert rate.fee == 0.0

def test_get_exchange_rate_closest_date(exchange_rate_service):
    """Test getting an exchange rate for a date that doesn't exist"""
    # Add a rate for a different date
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.25, 0.5, datetime(2023, 1, 22)))
    
    # Get rate for a date between the two existing rates - should return the closest
    rate = exchange_rate_service.get_exchange_rate("GBP", "USD", datetime(2023, 1, 21, 12))
    assert rate is not None
    assert rate.rate == 1.22  # Should return the rate from Jan 21
    
    # Get rate for a date after the latest - should return the latest
    rate = exchange_rate_service.get_exchange_rate("GBP", "USD", datetime(2023, 1, 23))
    assert rate is not None
    assert rate.rate == 1.25  # Should return the rate from Jan 22

def test_get_exchange_rate_inverse(exchange_rate_service):
    """Test getting an exchange rate by reversing an existing rate"""
    # We don't have a direct USD to GBP rate, but we have GBP to USD
    rate = exchange_rate_service.get_exchange_rate("USD", "GBP", datetime(2023, 1, 21))
    assert rate is not None
    assert rate.source == "USD"
    assert rate.target == "GBP"
    # The inverse of 1.22 should be approximately 0.82
    assert 0.81 < rate.rate < 0.83
    assert rate.fee == 0.5  # Fee should remain the same

def test_convert_to_eur_direct(exchange_rate_service):
    """Test converting a currency to EUR directly"""
    # GBP to EUR with 0.3% fee
    # 100 GBP - 0.3% fee = 99.7 GBP * 1.18 = 117.646 EUR
    amount_eur = exchange_rate_service.convert_to_eur(100, "GBP", datetime(2023, 1, 21))
    assert amount_eur is not None
    assert round(amount_eur, 2) == 117.65

def test_convert_to_eur_transitive(exchange_rate_service):
    """Test converting a currency to EUR via an intermediate currency"""
    # Create a service with only GBP to USD and USD to EUR rates (no direct GBP to EUR)
    service = ExchangeRateService()
    service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.22, 0.5, datetime(2023, 1, 21)))
    service.add_exchange_rate(ExchangeRate("USD", "EUR", 0.92, 0.4, datetime(2023, 1, 21)))
    
    # 100 GBP - 0.5% fee = 99.5 GBP * 1.22 = 121.39 USD
    # 121.39 USD - 0.4% fee = 120.9 USD * 0.92 = 111.23 EUR
    amount_eur = service.convert_to_eur(100, "GBP", datetime(2023, 1, 21))
    assert amount_eur is not None
    assert 111 < amount_eur < 112

def test_convert_to_eur_missing_rate():
    """Test attempting to convert with a missing rate"""
    service = ExchangeRateService()
    # Try to convert a currency with no rates
    amount_eur = service.convert_to_eur(100, "JPY", datetime(2023, 1, 21))
    assert amount_eur is None

def test_convert_to_eur_already_eur(exchange_rate_service):
    """Test converting EUR to EUR (should return the amount unchanged)"""
    amount_eur = exchange_rate_service.convert_to_eur(100, "EUR", datetime(2023, 1, 21))
    assert amount_eur == 100