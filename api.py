from donation_service import DonationService
from models import Donator, Charity
from datetime import datetime
from typing import Dict

class Api:
    def __init__(self, donation_service:DonationService):
        self.donation_service = donation_service

    def get_highest_grossing_charity_over_24_hours(self, end:datetime = None) -> Charity:
        """Get the highest grossing charity over the last 24 hours. Can pass in a custom date."""
        charity, total, donations = self.donation_service.get_highest_charity_over_24_hours(end)
        return {
            "charity" : charity,
            "total" : total,
            "donations" : donations
        }

    def get_most_generous_donator(self) -> Dict:
        """API endpoint to get the most generous donator."""
        return {
            "donator_id": self.donation_service.most_generous_donator.donator_id,
            "total_eur": self.donation_service.most_generous_donator.total_eur
        }

    def get_running_totals_for_all_charities(self) -> Dict:
        """API endpoint to get the running total for all charities and the global total"""
        return {
            "total_donations": self.donation_service.total_donations,
            "total_per_charity": {
                charity : self.donation_service.charities[charity].total_donations for charity in self.donation_service.charities
            }
        }