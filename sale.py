#!/usr/bin/python
import sys
import json
import decimal


class Item(object):
    def __init__(self, item_number, price, item_name):
        assert isinstance(item_number, str)
        assert isinstance(price, str)
        assert isinstance(item_name, str)
        self.item_number = item_number
        self.price = decimal.Decimal(price)
        self.item_name = item_name
        self.description = "Some description goes here"


#
# Inventory
# The order is useful; that's how they will be displayed on the page
#
items = [
    Item("plant1", "1.45", "Some Plant"),
    Item("plant2", "2.45", "Another Plant"),
    Item("plant3", "3.45", "Some Small Plant"),
    Item("plant4", "4.45", "Some Medium Plant"),
    Item("plant5", "5.45", "Some Large Plant"),

    Item("shrub1", "100.99", "Some Shrub"),
    Item("shrub2", "200.99", "Another Shrub"),

    Item("flower4", "4.99", "Flower Y"),
    Item("flower3", "3.99", "Flower X"),
    Item("flower2", "2.99", "Flower Two"),
    Item("flower1", "1.99", "Flower One"),
    ]


def get_item_by_name(name):
    for i in items:
        if i.name == name:
            return i
    raise Exception("Item %r not found" % name)
    

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
    <input type="hidden" name="item_number" value="%(item_number)s">
    <input type="hidden" name="amount" value="%(amount)s">

    <!-- Display the payment button. -->
    <input type="image" name="submit" border="0" src="https://www.paypalobjects.com/en_US/i/btn/btn_cart_LG.gif"
        alt="PayPal - The safer, easier way to pay online">
</form>
"""
    return s % dict(item_name=item.item_name, amount=item.price,
            item_number=item.item_number)


def get_item_display_info(item):
    s = """
<div class="item col-sm-6 col-md-4">
<img class="xxcenter-block img-responsive" src="images/zinnia.png"></img>
  <h4 class="xxtext-center">%(item_name)s</h4>
  <p>%(description)s</p>
  <p>Item Number: %(item_number)s</p>
  <b>$%(price)s&nbsp;&nbsp;</b>
  %(button)s
</div>
"""
    return s % dict(
        item_number=item.item_number,
        item_name=item.item_name, 
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
        if item.item_number.startswith(item_name_match):
            yield get_item_display_info(item)


def main():
    for l in sys.stdin:
        if l.strip().startswith("@{"):
            for l in expand(l):
                sys.stdout.write(l)
        else:
            sys.stdout.write(l)


if __name__ == "__main__":
    main()
