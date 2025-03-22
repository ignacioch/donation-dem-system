from models import Donation, Charity, Donator
from exchange_rate_service import ExchangeRateService
from datetime import datetime, timedelta
from typing import List, Tuple  

class DonationService:
    """A class representing a donation service."""
    def __init__(self, exchange_rate_service:ExchangeRateService):
        self.exchange_rate_service = exchange_rate_service
        "This is a global list of donations for all charities"
        self.donations = []

        self.charities = {} # Dict[charity_name, Charity]
        self.donators = {} # Dict[donator_name, Donator]

        # Highest donator across all donations (not only in a 24h window)
        self.most_generous_donator : Donator = None 
        # Total donations throught the service's lifetime
        self.total_donations = 0
    
    def add_donation(self, donation:Donation):
        if donation.amount_eur is None:
            # the original donation isn't in EUR so we need to convert it
            eur = self.exchange_rate_service.convert_to_eur(donation.amount, donation.currency, donation.timestamp)
            if eur is None:
                raise ValueError(f"No exchange rate available for {donation.currency} to EUR at {donation.timestamp})")
            donation.amount_eur = eur
        self.donations.append(donation)
        print(f"Added donation: {donation}")

        # Update running total
        # O(1) to keep total donations updates
        self.total_donations += donation.amount_eur

        # update charities
        # O(1) to keep total donations per charity updated
        if donation.charity not in self.charities:
            self.charities[donation.charity] = Charity(donation.charity)
        self.charities[donation.charity].add_donation(donation)

        # update donators
        if donation.donator not in self.donators:
            self.donators[donation.donator] = Donator(donation.donator)
        self.donators[donation.donator].add_donation(donation)

        # update statistics for donatos
        if self.most_generous_donator is None or self.most_generous_donator.total_eur < self.donators[donation.donator].total_eur:
            self.most_generous_donator = self.donators[donation.donator]

    
    def get_highest_charity_over_24_hours(self, end:datetime = None) -> Tuple[Charity, float, List[Donation]]:
        """Get the highest grossing charity over the last 24 hours. Can pass in a custom date."""
        window_start: datetime = end - timedelta(days=1) if end is not None else datetime.now() - timedelta(days=1)
        print(f"Getting highest charity over the last 24 hours starting from {window_start}")
        # filter donations in the last 24 hours
        total_donations_per_charity = {}
        donations_per_charity = {}
        for donation in self.donations:
            #print(f"Checking donation: {donation.timestamp} vs {window_start} and {end}")
            if donation.timestamp >= window_start and donation.timestamp <= end:
                total_donations_per_charity[donation.charity] = total_donations_per_charity.get(donation.charity, 0) + donation.amount_eur
                donations_per_charity[donation.charity] = donations_per_charity.get(donation.charity, []) + [donation]
                #print(f"Donations for {donation.charity}: {total_donations_per_charity[donation.charity]}")

        # get the highest grossing charity
        if total_donations_per_charity == {}:
            return (None, 0, [])
        
        highest_charity = max(total_donations_per_charity, key=total_donations_per_charity.get)
        #print(f"Highest charity: {highest_charity} with {total_donations_per_charity[highest_charity]}")
        # Sort the donations for the highest charity by timestamp
        donations_per_charity[highest_charity].sort(key=lambda d: d.timestamp)
        #print(f"Donations for {highest_charity}: {donations_per_charity[highest_charity]}")

        # Get the latest 5 donations
        latest_5_donations = donations_per_charity[highest_charity][-5:]
        #print(f"Latest 5 donations: {latest_5_donations}")
        return (highest_charity, total_donations_per_charity[highest_charity], latest_5_donations)
    



        
    