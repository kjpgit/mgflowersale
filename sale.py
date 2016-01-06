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
        self.options = None


def get_item_by_code(code):
    for i in g_items:
        if i.item_number == code:
            return i
    raise Exception("Item %r not found" % code)



#
# Inventory
# The order is useful; that's how they will be displayed on the page
#
g_items = [
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
    Item("flower7", "7.99", "Flower 7"),
    Item("flower8", "8.99", "Flower 8"),
    ]


# Special
get_item_by_code("plant2").description = \
      "A really long boring description one two three four blah foo baz blah foo baz hello"
get_item_by_code("plant3").description = ""




def get_view_cart_button():
    s = """
<!-- view cart button -->
<form class="navbar-form navbar-right" target="_self" action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">

    <!-- Identify your business so that you can collect the payments. -->
    <input type="hidden" name="business" value="karl.pickett-facilitator@gmail.com">

    <!-- Specify a PayPal Shopping Cart View Cart button. -->
    <input type="hidden" name="cmd" value="_cart">
    <input type="hidden" name="display" value="1">

    <!-- Display the View Cart button. -->
    <input type="image" name="submit" border="0"
        src="https://www.paypalobjects.com/en_US/i/btn/btn_viewcart_LG.gif"
       alt="PayPal - The safer, easier way to pay online">
</form>
"""
    return s
    

def get_buy_button(item):
    s = """
<!-- add to cart button -->
<form class="addcart" target="_self" action="https://www.sandbox.paypal.com/cgi-bin/webscr" method="post">
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
    """
    - 1 cols on xs (default)
    - 3 cols on small
    - 4 cols on md/lg
    """
    s = """
<div class="item col-sm-4 col-md-3">
<img class="xxcenter-block img-responsive" src="images/zinnia.png"></img>
  <h4 class="xxtext-center">%(item_name)s</h4>
  <p>%(description)s</p>
  <!--
  <p>Item Number: %(item_number)s</p>
  -->
  <div class="price"><b>$%(price)s&nbsp;&nbsp;</b></div>
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

    button = d.get("button", "")
    if button:
        assert button == "view_cart"
        yield get_view_cart_button()
    else:
        item_name_match = d["item_name_match"]
        n = 0
        for item in g_items:
            if item.item_number.startswith(item_name_match):
                yield get_item_display_info(item)
                n += 1
                if n % 4 == 0:
                  yield """<div class="clearfix visible-md-block visible-lg-block"></div>"""
                if n % 3 == 0:
                  yield """<div class="clearfix visible-sm-block"></div>"""



def main():
    for l in sys.stdin:
        if l.strip().startswith("@{"):
            for l in expand(l):
                sys.stdout.write(l)
        else:
            sys.stdout.write(l)


if __name__ == "__main__":
    main()
