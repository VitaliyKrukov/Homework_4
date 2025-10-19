import stripe

from config.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY


class StripeService:
    @staticmethod
    def create_product(name: str) -> str:
        try:
            product = stripe.Product.create(name=name)
            return product.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_price(product_id: str, amount: int, currency: str = "rub") -> str:
        try:
            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount,
                currency=currency,
            )
            return price.id
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_checkout_session(
        price_id: str, success_url: str, cancel_url: str
    ) -> dict:
        try:
            session = stripe.checkout.Session.create(
                line_items=[{"price": price_id, "quantity": 1}],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return {"session_id": session.id, "payment_link": session.url}
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def get_session_status(session_id: str) -> str:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session.payment_status
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
