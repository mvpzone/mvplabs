def place_order(client, sku: str, qty: int) -> str:
    order = client.submit_order(sku=sku, qty=qty)   # no such method on ShopClient
    return order["id"]
