class CardPayment:
    def pay(self, amount):
        return f"Paid {amount} by card"

class CashPayment:
    def pay(self, amount):
        return f"Paid {amount} by cash"

class PaymentFactory:
    @staticmethod
    def create(method):
        if method == "card":
            return CardPayment()
        elif method == "cash":
            return CashPayment()