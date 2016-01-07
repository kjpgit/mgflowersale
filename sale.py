#!/usr/bin/python
import cgi
import csv
import sys
import json
import decimal

g_items = []


class Item(object):
    def __init__(self, group, price, item_name, options, description, 
                quantity):
        assert isinstance(group, str)
        assert isinstance(price, str)
        assert isinstance(item_name, str)
        assert isinstance(description, str)
        assert isinstance(quantity, str)

        self.group = group
        self.price = decimal.Decimal(price)
        self.item_number = item_name
        self.item_name = item_name
        self.description = description
        self.quantity = quantity
        self.options = options


def escape(s):
    return cgi.escape(s, quote=True)


def load_data():
    f = open("data.txt", "rb")
    reader = csv.reader(f, delimiter=',', quotechar='"')
    n = 0
    for row in reader:
        n += 1
        if n == 1:
            continue
        parts = [x.strip() for x in row]
        assert len(parts) >= 6, "bad line %r" % row

        category = parts[0]
        quantity = parts[1]
        price = parts[2]
        item_name = parts[3]
        options = parts[4]
        description = parts[5]

        if not category:
            continue

        if not price:
            price = "0.00"

        if options:
            options = options.split(";")
            options = [x.strip() for x in options]
            options = ("Choose Option", options)

        item = Item(category, price, item_name, options, description,
                    quantity)
        try:
            load_item(item)
        except Exception as e:
            sys.stderr.write("Error in line %d: %r\n" % (n, row))
            raise e


def get_item_by_code(code):
    for i in g_items:
        if i.item_number == code:
            return i
    raise Exception("Item %r not found" % code)


def load_item(item):
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
    <!--
    <input type="hidden" name="item_number" value="%(item_number)s">
    -->
    <input type="hidden" name="amount" value="%(amount)s">

    <input type="hidden" name="no_shipping" value="1">
    <input type="hidden" name="return" value="http://karl:8002/thankyou.html">

    %(options)s

    <!-- Display the payment button. -->
    <input type="image" name="submit" border="0" 
        src="https://www.paypalobjects.com/en_US/i/btn/btn_cart_LG.gif"
        alt="PayPal - The safer, easier way to pay online">
</form>
"""
    options = ""
    if item.options:
        text = escape(item.options[0])
        options += """
            <input type="hidden" name="on0" value="%s"><b>%s:</b>
             <select name="os0">
            """ % (text, text)

        for opt in item.options[1]:
            options += """<option value="%(v)s">%(v)s</option>""" % \
                dict(v=escape(opt))

        options += """</select><br><div class=vspace></div>"""


    return s % dict(
            item_name=escape(item.item_name), 
            amount=item.price,
            item_number=escape(item.item_number), 
            options=options)


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
  <div class="price">
    <span class=quantity>%(quantity)s</span>
    &nbsp;-&nbsp;
    <b>$%(price)s</b>
    </div>
  %(button)s
</div>
"""
    return s % dict(
        item_number=item.item_number,
        item_name=item.item_name, 
        description=item.description,
        price=item.price,
        quantity=item.quantity,
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
