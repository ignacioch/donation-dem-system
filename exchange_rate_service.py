from models import ExchangeRate
from datetime import datetime

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
    
    def convert_to_eur(self, amount:float, currency:str, date:datetime) -> float:
        """Convert an amount from a currency to EUR based on the exchange rate of that date"""
        if currency == "EUR":
            return amount
    
        rate = self.get_exchange_rate(currency, "EUR", date)
        if rate is not None:
            return rate.convert(amount)
        else:
            #print(f"Could not convert {amount} {currency} to EUR on {date}. Trying hops.")
            # it means we didn't find a direct rate so let's try transitive conversion
            if currency == "USD":
                # first fgo USD to GBP
                rate1 = self.get_exchange_rate("USD", "GBP", date)
                if rate1 is not None:
                    amount_gbp = rate1.convert(amount)
                    # then go GBP to EUR
                    rate2 = self.get_exchange_rate("GBP", "EUR", date)
                    if rate2 is not None:
                        return rate2.convert(amount_gbp)
            elif currency == "GBP":
                # first go GBP to USD
                rate1 = self.get_exchange_rate("GBP", "USD", date)
                if rate1 is not None:
                    amount_usd = rate1.convert(amount)
                    # then go USD to EUR
                    rate2 = self.get_exchange_rate("USD", "EUR", date)
                    if rate2 is not None:
                        return rate2.convert(amount_usd)
            print(f"[FATAL]:Could not convert {amount} {currency} to EUR on {date}")
            return None

    
    def get_exchange_rate(self, source:str, target:str, date:datetime) -> ExchangeRate:
        """
        Get exchange rate for a specific date, source and target currency.
        If a rate isn't available for the specific date, the closest one is returned.
        """
        date_str = date.strftime("%Y-%m-%d")
        source_target = f"{source}_{target}"
        target_source = f"{target}_{source}" # For reverse rate
        #print(f"Searching direct rate for {source_target} on {date_str} ")

        # Case 1
        # if source and target are the same, return a rate of 1 (no fee)
        if source == target:
            #print(f"[case 1] : {source} == {target} so returning 1.0 (no fee)")
            return ExchangeRate(source, target, 1.0, 0.0, date)
        
        #print(f"[Case 2 checking] Trying to get exchange rate for {source} to {target} on {date_str}")
        # Case 2
        # if I have a direct rate, return it
        if date_str in self.exchange_rates:
            #print(f"We have exchange rates for {date_str}")
            if source_target in self.exchange_rates[date_str]:
                #print(f"[Case 2.1] : Found direct rate for {source_target} on {date_str} : {self.exchange_rates[date_str][source_target]}")
                return self.exchange_rates[date_str][source_target]
            elif target_source in self.exchange_rates[date_str]:
                #print(f"[Case 2.2] : Found direct rate for {target_source} on {date_str} : {self.exchange_rates[date_str][target_source]}")
                # Get the inverse rate
                inverse_rate = self.exchange_rates[date_str][target_source]
                # Create a new rate with inverted calculation
                # For inverted rate: 
                # - New rate is 1/old rate
                # - Fee needs special handling since it applies before conversion
                inverted_rate = 1 / inverse_rate.rate
                # We'll use the same fee for simplicity
                return ExchangeRate(source, target, inverted_rate, inverse_rate.fee, inverse_rate.date)
            #print(f"[Case 2.3] : No direct rate for {source_target} or {target_source} on {date_str}")
        
        # Case 3
        # what if I have no data for the specific date?
        # I could return the latest rate available
        closest_date = None
        for d in self.exchange_rates:
            d_date = datetime.strptime(d, "%Y-%m-%d")
            if source_target in self.exchange_rates[d]:
                if closest_date is None or abs((d_date - date).days) < abs((datetime.strptime(closest_date, "%Y-%m-%d") - date).days):
                    closest_date = d
        
        if closest_date is not None:
            return self.exchange_rates[closest_date][source_target]
        #print(f"[Case 3] : No exchange rate found for {source} to {target} on {date_str}")
        return None

