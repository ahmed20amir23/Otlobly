class PricingStrategy:
    def calculate(self, price, qty):
        pass

class NormalPricing(PricingStrategy):
    def calculate(self, price, qty):
        return price * qty

class DiscountPricing(PricingStrategy):
    def calculate(self, price, qty):
        return price * qty * 0.9