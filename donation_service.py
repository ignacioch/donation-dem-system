from models import Donation, Charity, Donator
from exchange_rate_service import ExchangeRateService
from datetime import datetime, timedelta

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

    def _validate_sliding_window(self, donation_timestamp:datetime):
        window_start = donation_timestamp - timedelta(days=1)
        # remove older ones
        while len(self.sliding_window_queue) > 0 and self.sliding_window_queue[0].timestamp < window_start:
            oldest = self.sliding_window_queue.pop(0)
            self.sliding_window_total_per_charity[oldest.charity] -= oldest.amount_eur
            if self.sliding_window_total_per_charity[oldest.charity] == 0:
                del self.sliding_window_total_per_charity[oldest.charity]
        # update highest grossing charity
        if len(self.sliding_window_queue) > 0:
            self.highest_grossing_charity = max(self.sliding_window_total_per_charity, key=self.sliding_window_total_per_charity.get)
        else:
            self.highest_grossing_charity = None

    
    def add_donation(self, donation:Donation):
        print("===============================================")
        print(f"(Trying) Adding donation: {donation}")
        if donation.amount_eur is None:
            # the original donation isn't in EUR so we need to convert it
            eur = self.exchange_rate_service.convert_to_eur(donation.amount, donation.currency, donation.timestamp)
            if eur is None:
                raise ValueError(f"No exchange rate available for {donation.currency} to EUR at {donation.timestamp})")
            donation.amount_eur = eur
            print(f"Converted {donation.amount} {donation.currency} to {donation.amount_eur} EUR")
        self.donations.append(donation)
        
        # Update running total
        # O(1) to keep total donations updates
        self.total_donations += donation.amount_eur
        print(f"Total donations({len(self.donations)}): {self.total_donations}")

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


        print("===============================================")
    
    def get_highest_charity_over_24_hours(self, end:datetime = None) -> Charity:
        """Get the highest grossing charity over the last 24 hours. Can pass in a custom date."""
        window_start: datetime = end - timedelta(days=1) if end is not None else datetime.now() - timedelta(days=1)
        print(f"Getting highest charity over the last 24 hours starting from {window_start}")
        # filter donations in the last 24 hours
        total_donations_per_charity = {}
        donations_per_charity = {}
        for donation in self.donations:
            if donation.timestamp >= window_start and donation.timestamp <= end:
                total_donations_per_charity[donation.charity] = total_donations_per_charity.get(donation.charity, 0) + donation.amount_eur
                donations_per_charity[donation.charity] = donations_per_charity.get(donation.charity, []) + [donation]

        # get the highest grossing charity
        highest_charity = max(total_donations_per_charity, key=total_donations_per_charity.get)
        # Sort the donations for the highest charity by timestamp
        donations_per_charity[highest_charity].sort(key=lambda d: d.timestamp)

        # Get the latest 5 donations
        latest_5_donations = donations_per_charity[highest_charity][-5:]
        return (highest_charity, self.charities[highest_charity], latest_5_donations)
    



        
    