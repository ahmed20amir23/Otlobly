class ExternalPaymentAPI:
    def make_payment(self, amount):
        return f"External paid {amount}"


class PaymentAdapter:
    def __init__(self, api):
        self.api = api

    def pay(self, amount):
        return self.api.make_payment(amount)