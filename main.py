import csv
from datetime import datetime, timedelta
import re
from models import Donation, ExchangeRate
from exchange_rate_service import ExchangeRateService
from donation_service import DonationService
from api import Api
from typing import List

class DataLoader:
    @staticmethod
    def parse_date(date_str:str)->datetime:
        """Parse date string in format '21 Jan 2023' to datetime object"""
        return datetime.strptime(date_str, "%d %b %Y")

    @staticmethod
    def parse_timestamp(timestamp_str:str)->datetime:
        """
        Parse timestamp string with timezone to UTC datetime object.
        Handles formats like '21 Jan 2023 10:15 EST'
        Supports EST, CET, and GMT timezones
        """
        # Extract timezone if present
        timezone_pattern = r'(EST|GMT|CET)$'
        timezone_match = re.search(timezone_pattern, timestamp_str)
        timezone = timezone_match.group(1) if timezone_match else None
    
        # Remove timezone from string for parsing
        timestamp_clean = re.sub(timezone_pattern, '', timestamp_str).strip()
        timestamp = datetime.strptime(timestamp_clean, "%d %b %Y %H:%M")
    
        # Convert to UTC based on timezone
        if timezone == "EST":  # Eastern Standard Time is UTC-5
            utc_offset_hours = -5
        elif timezone == "CET":  # Central European Time is UTC+1
            utc_offset_hours = 1
        elif timezone == "GMT":  # Greenwich Mean Time is UTC
            utc_offset_hours = 0
        else:
            utc_offset_hours = 0  # Default to UTC if no timezone
    
        # Use timedelta to correctly handle date rollovers
        utc_timestamp = timestamp + timedelta(hours=-utc_offset_hours)
    
        print(f"Converted {timestamp_str} ({timestamp}) to UTC: {utc_timestamp}")
        return utc_timestamp

    @staticmethod
    def load_exchange_rates(file_path:str)->List[ExchangeRate]:
        """Load exchange rates from CSV file"""
        exchange_rates = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                source = row['source']
                target = row['target']
                rate = float(row['rate'])
                fee = float(row['fee'])
                date = DataLoader.parse_date(row['date'])
                exchange_rates.append(ExchangeRate(source, target, rate, fee, date))
        return exchange_rates

    @staticmethod
    def load_donations(file_path:str)->List[Donation]:
        """Load donations from CSV file"""
        donations = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                donator = row['donator']
                amount = row['amount']
                charity = row['charity']
                timestamp = DataLoader.parse_timestamp(row['timestamp'])
                donations.append(Donation(donator, amount, charity, timestamp))
        return donations

def main():
    # Initialize services
    exchange_rate_service = ExchangeRateService()
    donation_service = DonationService(exchange_rate_service)
    
    # Load exchange rates
    exchange_rates = DataLoader.load_exchange_rates('exchange_rates.csv')
    for rate in exchange_rates:
        exchange_rate_service.add_exchange_rate(rate)
    
    # Load donations
    donations = DataLoader.load_donations('donations.csv')
    for donation in donations:
        donation_service.add_donation(donation)
    
    # Create API and use it
    api = Api(donation_service)
    print("\n=== API Results ===")
    print(f"Most generous donator: {api.get_most_generous_donator()}")
    print(f"Total donations: {api.get_running_totals_for_all_charities()}")
    
    # Test with specific timestamps
    print("\n=== 24-Hour Window Tests ===")
    print(f"Highest grossing charity at 2023-01-21 10:15: "
          f"{api.get_highest_grossing_charity_over_24_hours(datetime(2023, 1, 21, 10, 15))}")
    
    print(f"Highest grossing charity at 2023-01-23 10:15: "
          f"{api.get_highest_grossing_charity_over_24_hours(datetime(2023, 1, 23, 10, 15))}")


if __name__ == "__main__":
    main()