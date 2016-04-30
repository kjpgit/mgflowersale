#!/usr/bin/python
import cgi
import csv
import sys
import json
import decimal

from jinja2 import Environment, FileSystemLoader


g_items = []


class Item(object):
    def __init__(self, group, price, item_name, options, description, 
                quantity, image_file, min_quant):
        assert isinstance(group, str)
        assert isinstance(price, str)
        assert isinstance(item_name, str)
        assert isinstance(quantity, str)

        self.group = group
        self.price = decimal.Decimal(price)
        self.item_number = item_name
        self.item_name = item_name
        self.description = description
        self.quantity = quantity
        self.options = options
        self.image_file = image_file
        self.min_quant = int(min_quant)


def escape(s):
    return cgi.escape(s, quote=True)


def load_data():
    f = open("src/data.csv", "rb")
    reader = csv.reader(f, delimiter=',', quotechar='"')
    n = 0
    for row in reader:
        n += 1
        if n == 1:
            continue
        parts = [x.strip() for x in row]
        assert len(parts) >= 10, "bad line %r" % row

        category = parts[0]
        quantity = parts[1]
        price = parts[2]
        item_name = parts[3]
        options = parts[4]
        description = parts[5].decode("utf-8")
        image_file = parts[9]
        min_quant = parts[10]

        if not category:
            continue # blank row

        if not price:
            price = "0.00"
        if not image_file:
            image_file = "thumbs/under-construction.jpg"
        else:
            image_file = "thumbs/" + image_file

        if options:
            options = options.split(";")
            options = [x.strip() for x in options]
            options = ("Choose Option", options)

        item = Item(category, price, item_name, options, description,
                    quantity, image_file, min_quant)
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
    return ""
    s = """
<!-- view cart button -->
<form class="navbar-form navbar-right" target="_self" action="https://www.paypal.com/cgi-bin/webscr" method="post">

    <!-- Identify your business so that you can collect the payments. -->
    <input type="hidden" name="business" value="mg203treasurer@gmail.com">

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
    return ""
    s = """
<!-- add to cart button -->
<form class="addcart" target="_self" action="https://www.paypal.com/cgi-bin/webscr" method="post">
    <!-- Identify your business so that you can collect the payments. -->
    <input type="hidden" name="business" value="mg203treasurer@gmail.com">

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
    <!--
    <input type="hidden" name="return" value="http://karl:8002/thankyou.html">
    -->

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
            <input type="hidden" name="on0" value="Option"><b>%s:</b>
             <select name="os0">
            """ % (text,)

        for opt in item.options[1]:
            options += """<option value="%(v)s">%(v)s</option>""" % \
                dict(v=escape(opt))

        options += """</select><br><div class=vspace></div>"""

    # In the paypal cart, add a quantity description to the item name for
    # things that aren't single packs
    paypal_name = item.item_name
    quantity_helper = dict()
    quantity_helper["24 Plants (half flat)"] = " (Half Flat)"
    quantity_helper["6 Plants"] = " (6 Plants)"
    quantity_helper["4 Plants"] = " (4 Plants)"
    quantity_helper["3.5 Inch Pot"] = None
    quantity_helper["4.3 Inch Pot"] = None
    quantity_helper["Each"] = None
    extra = quantity_helper[item.quantity]
    if extra:
        paypal_name += extra

    return s % dict(
            item_name=escape(paypal_name), 
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
<img class="item-image img-responsive" src="%(image)s"></img>
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
        image=item.image_file,
        button=get_buy_button(item))


def get_items_g(filter):
    n = 0
    for item in g_items:
        if item.group.startswith(filter):
            yield get_item_display_info(item)
            # clearfix so columns of unequal height don't mess up layout
            n += 1
            if n % 4 == 0:
              yield """<div class="clearfix visible-md-block visible-lg-block"></div>"""
            if n % 3 == 0:
              yield """<div class="clearfix visible-sm-block"></div>"""


def get_items(filter):
    s = u""
    for i in get_items_g(filter):
        s += i
    return s


def crunch_orders2():
    f = open("Flower Sale CSV 4-14-16.csv", "rb")
    reader = csv.reader(f, delimiter=',', quotechar='"')
    row = reader.next()
    header = {}
    for k, v in enumerate(row):
        header[v.strip()] = k

    carts = {}
    for row in reader:
        parts = [x.strip() for x in row]

        def _get(t):
            return parts[header[t]]

        itype = _get("Type")
        txn = _get("Transaction ID")
        if itype in ("Shopping Cart Payment Received",):
            print itype, txn
            assert txn not in carts
            obj = {}
            obj["top"] = parts
            obj[""] = parts
            carts[txn] = {}

        if itype in ("Shopping Cart Item",):
            txns[txn].append(parts)

    print json.dumps(txns, indent=2)

    sys.exit(0)


def to_dict(row, header):
    parts = [x.strip() for x in row]
    ret = {}
    for k, v in enumerate(row):
        ret[header[k].strip()] = v.strip()
    return ret

def crunch_orders():
    f = open("Flower Sale CSV 4-14-16.csv", "rb")
    reader = csv.reader(f, delimiter=',', quotechar='"')
    header = reader.next()

    total = 0
    groups = {}
    min_quants = {}

    for row in reader:
        obj = to_dict(row, header)
        if obj["Type"] == "Shopping Cart Item":
            quant = int(obj["Quantity"])
            assert quant >= 1
            title = obj["Item Title"]
            real_title = title.replace(" (4 Plants)", "")
            real_title = real_title.replace(" (6 Plants)", "")
            real_title = real_title.replace(" (Half Flat)", "")
            item = get_item_by_code(real_title)
            option = obj["Option 1 Value"]
            if option:
                title += " " + option
            if title not in groups:
                groups[title] = 0
                min_quants[title] = item.min_quant
            groups[title] += quant
            total += quant * item.price
            #print json.dumps(obj, indent=2)


    for k in sorted(groups.keys()):
        quant = groups[k]
        min_quant = min_quants[k]

        rounded = quant
        diff = quant % min_quant
        if diff:
            rounded += (min_quant - diff)
        print "%s,%s,%s,%s" % (k, quant, min_quant, rounded)

    print "---"
    print "TOTAL Retail Price of Items", total


def print_orders():
    #f = open("Flower Sale CSV 4-14-16.csv", "rb")
    f = open("/tmp/Individual.csv", "rb")
    reader = csv.reader(f, delimiter=',', quotechar='"')
    header = reader.next()

    total = 0
    groups = {}

    for row in reader:
        obj = to_dict(row, header)
        if obj["Type"] == "Shopping Cart Item":
            if obj["Status"] not in ("Completed", "Cleared", "Uncleared"):
                raise Exception("bad", obj)

            person = obj["From Email Address"].lower()
            if not person:
                person = obj["Name"]
            if person not in groups:
                groups[person] = []

            groups[person].append(obj)

    people = groups.keys()
    people.sort()

    print """
    <html>

    <head>
    <style>
    td { min-width: 40px; padding: 4px; }
    .dum { min-width: 30px; }

    table, th, td { border: 1px solid black;     border-collapse: collapse; }
    h1, h2 { display: inline-block; }
    </style>
    </head>

    <body>
    """.strip()

    n = 0
    for k in people:
        n += 1
        orders = groups[k]
        print "<h1>#%s&nbsp;&nbsp;</h1>" % n
        print "<h2>%s (%s)</h2>" % (orders[0]["Name"], k)
        print "<table>"
        for item in sorted(orders, key=lambda x: x["Item Title"].lower()):
            #print json.dumps(item, indent=2)
            dump_pickup_item(item)
        print "</table>"
        print '<p style="page-break-after:always;"></p>'

    print """
    </body>
    </html>
    """.strip()

    sys.exit(0)


def dump_pickup_item(obj):
    quant = int(obj["Quantity"])
    assert quant >= 1
    title = obj["Item Title"]
    option = obj["Option 1 Value"]
    print "<tr><td class='dum'><td>%s<td>%s<td>%s</tr>" % (
            escape(title), option, quant)




def main():
    load_data()
    #crunch_orders()
    print_orders()
    env = Environment(loader=FileSystemLoader('src/templates'))
    env.globals['get_view_cart_button'] = get_view_cart_button
    env.globals['get_items'] = get_items

    template = env.get_template('index.html')
    out = template.render()
    with open("index.html", "w") as f:
        f.write(out.encode("utf-8"))

    template = env.get_template('info.html')
    out = template.render()
    with open("info.html", "w") as f:
        f.write(out.encode("utf-8"))


if __name__ == "__main__":
    main()
