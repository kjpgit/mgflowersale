#!/usr/bin/python
import sys
import json
import decimal

g_items = []


#
# Inventory
# The order is useful; that's how they will be displayed on the page
#
def load_data():
    load_item("plant1", "1.45", "Some Plant")
    load_item("plant2", "2.45", "Another Plant")
    load_item("plant3", "3.45", "Some Small Plant")
    load_item("plant4", "4.45", "Some Medium Plant")
    load_item("plant5", "5.45", "Some Large Plant")

    load_item("shrub1", "100.99", "Some Shrub")
    load_item("shrub2", "200.99", "Another Shrub")

    load_item("flower4", "4.99", "Flower Y")
    load_item("flower3", "3.99", "Flower X")
    load_item("flower2", "2.99", "Flower Two")
    load_item("flower1", "1.99", "Flower One")
    load_item("flower7", "7.99", "Flower 7")
    load_item("flower8", "8.99", "Flower 8")


    # Special
    get_item_by_code("plant2").description = (
          "A really long boring description one two "
          "three four blah foo baz blah foo baz hello"
          "alpha beta gamma zebra doh blah foo baz blah hello")
    get_item_by_code("plant3").description = ""

    get_item_by_code("shrub1").description = (
          "A really long boring description one two "
          "three four blah foo baz blah foo baz hello"
          "alpha beta gamma zebra doh blah foo baz blah hello")
    get_item_by_code("shrub2").description = (
          "A really long boring description one two "
          "three four blah foo baz blah foo baz hello")

    get_item_by_code("shrub2").options = \
            ("Color", ["Red", "Blue", "Pink", "White"])



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


def load_item(*args, **kwargs):
    item = Item(*args, **kwargs)
    for i in g_items:
        if i.item_number == item.item_number:
            raise Exception("Duplicate item_number %r" % i.item_number)
        if i.item_name == item.item_name:
            raise Exception("Duplicate item_name %r" % i.item_name)
    g_items.append(item)


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

    %(options)s

    <!-- Display the payment button. -->
    <input type="image" name="submit" border="0" 
        src="https://www.paypalobjects.com/en_US/i/btn/btn_cart_LG.gif"
        alt="PayPal - The safer, easier way to pay online">
</form>
"""
    options = ""
    if item.options:
        options += """
            <br>
            <input type="hidden" name="on0" value="%s"><b>Choose %s:</b>
             <select name="os0">
            """ % (item.options[0], item.options[0])

        for opt in item.options[1]:
            options += """<option value="%(v)s">%(v)s</option>""" % dict(v=opt)

        options += """</select><br><div class=vspace></div>"""


    return s % dict(item_name=item.item_name, amount=item.price,
            item_number=item.item_number, options=options)


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
                # clearfix so columns of unequal height don't mess up layout
                n += 1
                if n % 4 == 0:
                  yield """<div class="clearfix visible-md-block visible-lg-block"></div>"""
                if n % 3 == 0:
                  yield """<div class="clearfix visible-sm-block"></div>"""


def main():
    load_data()
    for l in sys.stdin:
        if l.strip().startswith("@{"):
            for l in expand(l):
                sys.stdout.write(l)
        else:
            sys.stdout.write(l)


if __name__ == "__main__":
    main()
