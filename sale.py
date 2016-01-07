#!/usr/bin/python
import sys
import json
import decimal

g_items = []


class Item(object):
    def __init__(self, group, price, item_name, options):
        assert isinstance(group, str)
        assert isinstance(price, str)
        assert isinstance(item_name, str)
        self.group = group
        self.item_number = item_name
        self.price = decimal.Decimal(price)
        self.item_name = item_name
        self.description = "Some description goes here"
        self.options = options



def load_data():
    for l in open("data.txt"):
        l = l.strip()
        if not l:
            continue
        parts = l.split(",")
        assert len(parts) in (2, 3)

        code = parts[0].strip()
        name = parts[1].strip()
        options = None
        if len(parts) > 2:
            options = parts[2].split(";")
            options = [x.strip() for x in options]
            options = ("Choose Option", options)

        load_item(code, "5.99", name, options)


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
            <input type="hidden" name="on0" value="%s"><b>%s:</b>
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
            if item.group.startswith(item_name_match):
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
