#!/usr/bin/python
import sys
import json
import decimal


class Item(object):
    def __init__(self, name, price, desc):
        assert isinstance(name, str)
        assert isinstance(price, str)
        assert isinstance(desc, str)
        self.name = name
        self.price = decimal.Decimal(price)
        self.description = desc


items = [
    Item("plant1", "1.45", "Some Plant"),
    Item("plant2", "2.45", "Another Plant"),
    Item("shrub1", "100.99", "Some Shrub"),
    Item("shrub2", "200.99", "Another Shrub"),
    Item("flower1", "1.99", "Flower One"),
    Item("flower2", "2.99", "Flower Two"),
    Item("flower3", "3.99", "Flower X"),
    Item("flower4", "4.99", "Flower Y"),
    ]


def get_item_by_name(name):
    for i in items:
        if i.name == name:
            return i
    return Item(name, "0.00", "No Description")
    

def get_buy_button(item):
    s = """
<!-- add to cart button -->
<form target="_self" action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">

    <!-- Identify your business so that you can collect the payments. -->
    <input type="hidden" name="business" value="karl.pickett-facilitator@gmail.com">

    <!-- Specify a PayPal Shopping Cart Add to Cart button. -->
    <input type="hidden" name="cmd" value="_cart">
    <input type="hidden" name="add" value="1">

    <!-- Specify details about the item that buyers will purchase. -->
    <input type="hidden" name="item_name" value="%(item_name)s">
    <input type="hidden" name="amount" value="%(amount)s">

    <!-- Display the payment button. -->
    <input type="image" name="submit" border="0" src="https://www.paypalobjects.com/en_US/i/btn/btn_cart_LG.gif"
        alt="PayPal - The safer, easier way to pay online">
    <img alt="" border="0" width="1" height="1"
        src="https://www.paypalobjects.com/en_US/i/scr/pixel.gif" >
</form>
"""
    return s % dict(item_name=item.name, amount=item.price)


def get_buy_item(item):
    s = """
<div class="col-md-4">
  <h2>%(name)s - %(price)s</h2>
  <p>%(description)s</p>
  %(button)s
</div>
"""
    return s % dict(name=item.name, 
        description=item.description,
        price=item.price,
        button=get_buy_button(item))


def expand(l):
    l = l.strip()
    assert l.startswith("@{")
    assert l.endswith("}")
    l = l.strip()[1:]
    d = json.loads(l)

    item_name_match = d["item_name_match"]
    for item in items:
        if item.name.startswith(item_name_match):
            yield get_buy_item(item)


def main():
    for l in sys.stdin:
        if l.strip().startswith("@{"):
            for l in expand(l):
                sys.stdout.write(l)
        else:
            sys.stdout.write(l)


if __name__ == "__main__":
    main()
