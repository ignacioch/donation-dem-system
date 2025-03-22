import pytest
from datetime import datetime, timedelta
from models import Donation
from exchange_rate_service import ExchangeRateService
from donation_service import DonationService

@pytest.fixture
def exchange_rate_service():
    """Create an exchange rate service with test data"""
    from models import ExchangeRate
    
    service = ExchangeRateService()
    
    # Add exchange rates for test dates
    service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.18, 0.3, datetime(2023, 1, 20)))
    service.add_exchange_rate(ExchangeRate("USD", "EUR", 0.92, 0.4, datetime(2023, 1, 20)))
    service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.18, 0.3, datetime(2023, 1, 21)))
    service.add_exchange_rate(ExchangeRate("USD", "EUR", 0.92, 0.4, datetime(2023, 1, 21)))
    service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.18, 0.3, datetime(2023, 1, 22)))
    service.add_exchange_rate(ExchangeRate("USD", "EUR", 0.92, 0.4, datetime(2023, 1, 22)))
    
    return service

@pytest.fixture
def donation_service(exchange_rate_service):
    """Create a donation service with test data"""
    service = DonationService(exchange_rate_service)
    
    # Add some test donations
    timestamp_base = datetime(2023, 1, 21, 12, 0)
    
    # Add donations on day 1 (Jan 21)
    service.add_donation(Donation("User1", "$10", "Charity1", timestamp_base - timedelta(hours=2)))
    service.add_donation(Donation("User2", "£15", "Charity2", timestamp_base))
    service.add_donation(Donation("User1", "€5", "Charity1", timestamp_base + timedelta(hours=1)))
    
    # Add donations on day 2 (Jan 22)
    service.add_donation(Donation("User3", "$20", "Charity1", timestamp_base + timedelta(days=1)))
    service.add_donation(Donation("User2", "£10", "Charity2", timestamp_base + timedelta(days=1, hours=2)))
    
    return service

def test_add_donation(exchange_rate_service):
    """Test adding a donation to the service"""
    service = DonationService(exchange_rate_service)
    donation = Donation("User1", "$10", "Charity1", datetime(2023, 1, 21, 12, 0))
    
    # Verify initial state
    assert len(service.donations) == 0
    assert len(service.charities) == 0
    assert len(service.donators) == 0
    
    # Add donation
    service.add_donation(donation)
    
    # Verify updated state
    assert len(service.donations) == 1
    assert "Charity1" in service.charities
    assert "User1" in service.donators
    
    # Check that the donation was properly converted to EUR
    assert donation.amount_eur is not None
    # $10 - 0.4% fee = $9.96 * 0.92 = €9.16
    assert 9.1 < donation.amount_eur < 9.2

def test_get_highest_charity_over_24_hours(donation_service):
    """Test getting the highest grossing charity over 24 hours"""
    # Reference time is Jan 21, 12:00
    reference_time = datetime(2023, 1, 21, 12, 0)
    
    # Get highest charity
    charity_id, total_donations, donations = donation_service.get_highest_charity_over_24_hours(reference_time)
    # Check results
    # Charity1 received $10, Charity2 received £15
    assert charity_id == "Charity2"  
    assert len(donations) <= 5
    assert 17 < total_donations < 18
    
    # Reference time is Jan 22, 12:00
    reference_time = datetime(2023, 1, 22, 12, 0)
    
    # Get highest charity
    charity_id, total_donations, donations = donation_service.get_highest_charity_over_24_hours(reference_time)
    # Check results 
    # Charity 1 - €5 + $20  
    # Charity 2 - £15
    assert charity_id == "Charity1"  # Charity1 adds $20 on day 2
    assert len(donations) <= 5
    assert 23 < total_donations < 24

def test_running_totals(donation_service):
    """Test that running totals are correctly maintained"""
    # Add a new donation
    donation_service.add_donation(Donation("User4", "£20", "Charity3", datetime(2023, 1, 22, 12, 0)))
    
    # Check charity totals
    assert "Charity1" in donation_service.charities
    assert "Charity2" in donation_service.charities
    assert "Charity3" in donation_service.charities
    
    charity1 = donation_service.charities["Charity1"]
    charity2 = donation_service.charities["Charity2"]
    charity3 = donation_service.charities["Charity3"]
    
    # Charity1: $10 + €5 + $20
    # Charity2: £15 + £10
    # Charity3: £20
    
    # Verify these rough values (exact values depend on exchange rates and fees)
    assert 30 < charity1.total_donations < 35  # Approximately $10 + €5 + $20 in EUR
    assert 25 < charity2.total_donations < 30  # Approximately £15 + £10 in EUR
    assert 20 < charity3.total_donations < 25  # Approximately £20 in EUR

def test_most_generous_donator(donation_service):
    """Test getting the most generous donator"""
    # Initially User2 should be the most generous with £15 + £10
    assert donation_service.most_generous_donator is not None
    assert donation_service.most_generous_donator.donator_id == "User2"
    
    # Add a large donation from User4
    donation_service.add_donation(Donation("User4", "$50", "Charity1", datetime(2023, 1, 22, 14, 0)))
    
    # Now User4 should be the most generous
    assert donation_service.most_generous_donator.donator_id == "User4"

def test_empty_donation_service():
    """Test behavior with no donations"""
    service = DonationService(ExchangeRateService())
    
    # Highest charity should handle empty case
    result = service.get_highest_charity_over_24_hours(datetime(2023, 1, 21, 12, 0))
    
    assert result[0] is None and result[1] == 0 and result[2] == []
    
    # Most generous donator should be None
    assert service.most_generous_donator is None

def test_donations_in_time_window(donation_service):
    """Test filtering donations by time window"""
    # Add donations across multiple days
    day1 = datetime(2023, 1, 20, 12, 0)
    day2 = datetime(2023, 1, 21, 12, 0)
    day3 = datetime(2023, 1, 22, 12, 0)
    
    donation_service.add_donation(Donation("UserA", "$25", "CharityX", day1))
    donation_service.add_donation(Donation("UserB", "$20", "CharityX", day2))
    donation_service.add_donation(Donation("UserC", "$15", "CharityX", day3))
    
    # Get highest charity with reference time at day2
    charity_id, _, donations = donation_service.get_highest_charity_over_24_hours(day2)
    
    # Valid donations are :
    # Charity1: $10
    # Charity2: £15
    # ChartiyX : 20$ + 25$ = 45$

    # Should include day1 and day2 donations but not day3 for CharityX
    donation_timestamps = [d.timestamp for d in donations]
    assert any(t == day1 for t in donation_timestamps)
    assert any(t == day2 for t in donation_timestamps)
    assert not any(t == day3 for t in donation_timestamps)

    assert charity_id == "CharityX"
    assert (len(donations) == 2)