from datetime import datetime
import re

class ExchangeRate:
    """Class the represents a currency exchnage rate at a specific date"""
    def __init__(self, source:str, target:str, rate:float, fee:float, date:datetime):
        self.source : str = source
        self.target : str = target
        self.rate : float = rate
        self.fee : float = fee
        self.date : datetime = date
    
    def convert(self, amount:float) -> float:
        fee = amount * self.fee / 100
        return (amount-fee) * self.rate
    
    def __repr__(self):
        return f"ExchangeRate({self.source}_{self.target}, {self.rate}, {self.fee}%, {self.date})"
    
class Donation:
    """A class representing a donation."""
    def __init__(self, donator:str, amount:str, charity:str, timestamp:datetime):
        self.donator : str = donator
        self.charity : str = charity
        self.timestamp : datetime = timestamp

        # Parse amount string to extract currency and amount
        currency_pattern = r'^([£$€])(\d+(\.\d+)?)$'
        match = re.match(currency_pattern, amount)

        if match:
            currency_symbol = match.group(1)
            amount_value = match.group(2)
            
            # Map currency symbol to currency code
            currency_map = {
                '$': 'USD',
                '£': 'GBP',
                '€': 'EUR'
            }
            
            self.currency = currency_map.get(currency_symbol, 'USD')
            self.amount = float(amount_value)
        else:
            # If no match, try to extract numeric value and assume USD
            numeric_pattern = r'(\d+(\.\d+)?)'
            num_match = re.search(numeric_pattern, amount)
            
            if num_match:
                self.amount = float(num_match.group(1))
                self.currency = 'USD'  # Default to USD
            else:
                raise ValueError(f"Invalid amount format: {amount}")
        # will be updated from add_donation if we are not in EUR
        self.amount_eur : float|None = None if self.currency != 'EUR' else self.amount 
        
    
    def __str__(self):
        return f"{self.donator} donated {self.amount}{self.currency} to charity {self.charity} at {self.timestamp}"
    
    def __repr__(self):
        if self.amount_eur is not None:
            return f"Donation({self.donator}, {self.amount} {self.currency} ({self.amount_eur} EUR), {self.charity}, {self.timestamp})"
        else:
            return f"Donation({self.donator}, {self.amount} {self.currency}, {self.charity}, {self.timestamp})"
        
class Charity:
    """A class representing a charity."""
    def __init__(self, name:str):
        self.name : str = name
        self.total_donations : float = 0
        self.donations = []
    
    def add_donation(self, donation:Donation):
        self.donations.append(donation)
        self.total_donations += donation.amount_eur
        print(f"Total donations for {self.name}({len(self.donations)}): {self.total_donations}")
    
    def __repr__(self):
        return f"Charity({self.name}, {self.total_donations})"

class Donator:
    """Represents a donator with a running total of donations."""
    def __init__(self, donator_id: str):
        self.donator_id = donator_id
        self.total_eur : float = 0
        self.donation_count = 0
    
    def add_donation(self, donation: 'Donation') -> None:
        """Add a donation from this donator and update the running total."""
        self.total_eur += donation.amount_eur
        self.donation_count += 1
    
    def __repr__(self):
        return f"Donator({self.donator_id}, {self.total_eur} EUR, {self.donation_count} donations)"
  

    
