from datetime import datetime
from models import Donation, ExchangeRate
from exchange_rate_service import ExchangeRateService
from donation_service import DonationService
from api import Api

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

    api = Api(donation_service)
    print(f"Most generous donator: {api.get_most_generous_donator()}")
    print(f"Total donations: {api.get_running_totals_for_all_charities()}")
    print(f"Highest grossing charity: {api.get_highest_grossing_charity_over_24_hours(datetime(2023, 1, 21, 10, 15))}")
    print(f"Highest grossing charity: {api.get_highest_grossing_charity_over_24_hours(datetime(2023, 1, 23, 10, 15))}")



if __name__ == "__main__":
    main()

