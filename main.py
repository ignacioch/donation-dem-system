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
    

class ExchangeRateService:
    """Class that represents a service that provides exchange rates"""
    def __init__(self):
        self.exchange_rates = {}
    
    def add_exchange_rate(self, exchange_rate:ExchangeRate):
        """Add an exchange rate to the service"""
        date_str = exchange_rate.date.strftime("%Y-%m-%d")
        source_target = f"{exchange_rate.source}_{exchange_rate.target}"
        if date_str not in self.exchange_rates:
            self.exchange_rates[date_str] = {}
        
        self.exchange_rates[date_str][source_target] = exchange_rate
        print(f"Added [{date_str}][{source_target}] exchange rate= {exchange_rate}")
    
    def get_exchange_rate(self, source:str, target:str, date:datetime) -> ExchangeRate:
        """
        Get exchange rate for a specific date, source and target currency.
        If a rate isn't available for the specific date, the closest one is returned.
        If a dirct rate isn't available, the service will try to convert the source currency to the target currency
        using intermediate currencies.
        """
        date_str = date.strftime("%Y-%m-%d")
        source_target = f"{source}_{target}"

        # Case 1
        # if source and target are the same, return a rate of 1 (no fee)
        if source == target:
            return ExchangeRate(source, target, 1.0, 0.0, date)

        # Case 2
        # if I have a direct rate, return it
        if date_str in self.exchange_rates and source_target in self.exchange_rates[date_str]:
            return self.exchange_rates[date_str][source_target]

        
        # Case 3
        # what if I have no data for the specific date?
        # I could return the latest rate available
        closest_date = None
        for d in self.exchange_ratesrates:
            d_date = datetime.strptime(d, "%Y-%m-%d")
            if source_target in self.rates[d]:
                if closest_date is None or abs((d_date - date).days) < abs((datetime.strptime(closest_date, "%Y-%m-%d") - date).days):
                    closest_date = d
        
        if closest_date is not None:
            return self.exchange_rates[closest_date][source_target]
        
        # Case 4
        # Find a path through another currency
        return self._find_conversion_path(source, target, date)

    def _find_conversion_path(self, source:str, target:str, date:datetime) -> ExchangeRate:
        """
        Find a path to convert from source to target currency.
        In the examples provided we only have few pairs so might be easier to just hardcode the paths.
        But we will implement a generic solution that can work with any number of currencies, which will 
        involve calling BFS.
        """
        visited = set()
        queue = [(source,1.0,0.0,[])] #currency, rate so far, fee so far, path so far

        while queue:
            current_currency, cumul_rate, cumul_fee, path = queue.pop(0)
            if current_currency == target:
                return ExchangeRate(source, target, cumul_rate, cumul_fee, date)

            # we have already visited this currency
            if current_currency in visited:
                continue

            visited.add(current_currency)
            # find the neighbours of the current currency


        
        return None

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
            self.amount = amount_value
        else:
            # If no match, try to extract numeric value and assume USD
            numeric_pattern = r'(\d+(\.\d+)?)'
            num_match = re.search(numeric_pattern, amount)
            
            if num_match:
                self.amount = num_match.group(1)
                self.currency = 'USD'  # Default to USD
            else:
                raise ValueError(f"Invalid amount format: {amount}")
        # will be updated from add_donation if we are not in EUR
        self.amount_eur : float|None = None if self.currency != 'EUR' else self.amount 
        
    
    def __str__(self):
        return f"{self.donator} donated {self.amount}{self.currency} to charity {self.charity_id} at {self.timestamp}"
    
    def __repr__(self):
        if self.amount_eur is not None:
            return f"Donation({self.donator_id}, {self.amount} {self.currency} ({self.amount_eur} EUR), {self.charity_id}, {self.timestamp})"
        else:
            return f"Donation({self.donator_id}, {self.amount} {self.currency}, {self.charity_id}, {self.timestamp})"
  

class DonationService:
    """A class representing a donation service."""
    def __init__(self, exchange_rate_service:ExchangeRateService):
        self.exchange_rate_service = exchange_rate_service
        "This is a global list of donations for all charities"
        self.donations = []

        self.charities = {} # Dict[charity_name, Charity]
        self.donators = {} # Dict[donator_name, Donator]


        # Sliding window for tracking highest grossing charities
        self.last_24h_window_start = None
        self.highest_charity_24h = None
        self.highest_amount_24h = 0
        self.most_generous_donator = None 
        self.most_generous_amount = 0

        self.total_donations = 0

    
    def add_donation(self, donation:Donation):
        if donation.amount_eur is None:
            # the original donation isn't in EUR so we need to convert it
            rate = self.exchange_rate_service.get_exchange_rate(donation.currency, "EUR", donation.timestamp)
            donation.amount_eur = rate.convert(donation.amount)
        print(f"Adding donation: {donation}")
        self.donations.append(donation)
        
        # Update running total
        self.total_donations += donation.amount_eur
        print(f"Total donations({len(self.donations)}): {self.total_donations}")
        
    

def main():
    exchange_rate_service = ExchangeRateService()
    donation_service = DonationService(exchange_rate_service)

    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.26, 0.5, datetime(2023, 1, 20)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.17, 0.3, datetime(2023, 1, 20)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.22, 0.5, datetime(2023, 1, 21)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.18, 0.3, datetime(2023, 1, 21)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.23, 0.5, datetime(2023, 1, 22)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.14, 0.3, datetime(2023, 1, 22)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "USD", 1.26, 0.5, datetime(2023, 1, 23)))
    exchange_rate_service.add_exchange_rate(ExchangeRate("GBP", "EUR", 1.17, 0.3, datetime(2023, 1, 23)))


    # Add some donations
    donation_service.add_donation(Donation("User1","$10","Cancer Research", datetime(2023, 1, 21, 10, 15)))
    donation_service.add_donation(Donation("User2", "£15", "Wildlife conservation", datetime(2023, 1, 21, 12, 11)))
    donation_service.add_donation(Donation("User3", "€4", "Literacy at home", datetime(2023, 1, 23, 10, 7)))
    donation_service.add_donation(Donation("User4", "$10", "Literacy at home", datetime(2023, 1, 22, 23, 50)))
    donation_service.add_donation(Donation("User3", "€2","Cancer Research", datetime(2023, 1, 21, 10, 37)))
    donation_service.add_donation(Donation("User1", "£5", "Wildlife conservation", datetime(2023, 1, 20, 12, 53)))

    print(donation_service.total_donations)


if __name__ == "__main__":
    main()

