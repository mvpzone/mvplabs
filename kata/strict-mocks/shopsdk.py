"""A tiny stand-in for a vendor SDK: the real surface your code depends on."""


class ShopClient:
    def create_order(self, sku: str, qty: int) -> dict:
        raise RuntimeError("network call: not available in tests")

    def get_order(self, order_id: str) -> dict:
        raise RuntimeError("network call: not available in tests")
