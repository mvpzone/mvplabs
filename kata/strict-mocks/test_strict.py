from unittest.mock import create_autospec

from checkout import place_order
from shopsdk import ShopClient


def test_place_order_returns_the_id():
    client = create_autospec(ShopClient, instance=True)
    client.create_order.return_value = {"id": "ord-1"}
    assert place_order(client, "sku-42", 1) == "ord-1"
    client.create_order.assert_called_once_with(sku="sku-42", qty=1)
