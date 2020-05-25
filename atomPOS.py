import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import *
import csv
import datetime as datetime
from datetime import date
from datetime import datetime as dt
import pandas as pd
import numpy

STORE_NAME = "Code in Place Cafe"
PRODUCTS_FILE = 'code_in_place_cafe_products.csv'
PARTS_FILE = 'code_in_place_cafe_product_parts.csv'
INVENTORY_FILE = 'code_in_place_cafe_inventory.csv'
ORDER_DATA = 'orders.csv'
ITEMS_DATA = 'items_ordered.csv'
order_number = 0


def main():
    display_dashboard()


def display_dashboard():
    # Create and configure canvas and widget styles
    canvas = tk.Tk()
    canvas.title(STORE_NAME + ' Mini POS Dashboard')
    Grid.rowconfigure(canvas, 0, weight=1)
    Grid.columnconfigure(canvas, 0, weight=1)
    style = ttk.Style()
    style.configure('TFrame', background='white')
    style.configure('TLabel', background='white', foreground='black')
    style.configure('green.TButton', background='#e3f4e9', foreground='#23a74f', font='-weight bold')
    style.configure('red.TButton', background='#ffe0e6', foreground='#ff0838')
    style.configure('grey.TButton', background='white', foreground='#808080')

    # Create tabs on the display
    tab_control = ttk.Notebook(canvas)
    tab_control.grid(row=0, column=0, sticky=N + S + E + W)

    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Display Menu')

    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Active Cart')

    tab3 = ttk.Frame(tab_control)
    tab_control.add(tab3, text='Past Orders')

    tab4 = ttk.Frame(tab_control)
    tab_control.add(tab4, text='Inventory Status')

    tab_control.grid()

    # TODO: Overall structuring of data flow is messy, need to fix it to reduce inefficient loops
    fill_tabs(tab_control, tab1, tab2, tab3, tab4)

    canvas.mainloop()


# Display products and their details from a csv file
def fill_tabs(tab_control, tab1, tab2, tab3, tab4):
    for widget in tab1.winfo_children():
        widget.destroy()

    items_ordered = []
    entries = []

    # Display product details on the first tab - 'Display Menu'
    with open(PRODUCTS_FILE, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        c = 0
        for x in reader.fieldnames:
            header = ttk.Label(tab1, text=x, font='-weight bold')
            header.grid(row=0, column=c, padx=5, pady=5)
            c += 1
        menu_header = ttk.Label(tab1, text='enter_qty', font='-weight bold')
        menu_header.grid(row=0, column=c, padx=5, pady=5)

        r = 1
        e = 0

        for line in reader:
            c = 0
            for elem in line:
                menu_items = ttk.Label(tab1, text=line[elem])
                menu_items.grid(row=r, column=c, padx=5, pady=5)
                c += 1
            # Check stock and display 'Out of stock'
            check_stock = check_stock_zero(r)
            if not numpy.prod(check_stock):
                out_of_stock = ttk.Label(tab1, text='Out of stock')
                out_of_stock.grid(row=r, column=c, padx=5, pady=5)
            else:
                # Input fields for user input on display menu
                entries.append(Entry(tab1, width=5))
                ent = entries[e]
                ent.grid(row=r, column=c, padx=5, pady=5)
                e += 1
            r += 1

        # Capture order details when a user clicks 'Add to cart' button
        def add_to_cart():
            # If no inputs given by the user, show error message and return
            if check_for_blank_entries(entries):
                messagebox.showinfo("Message", "One does not simply place an order with empty inputs.")
                return

            # TODO: Check if all items are serviceable in full, else ask for inputs again (i.e. limited stock cases)

            # List items ordered
            list_items_ordered(entries, items_ordered)

            # Clear previous entries
            for entry in entries:
                entry.delete(0, END)

            # Display items added to cart, Confirm order button or cancel
            display_cart(items_ordered, tab1, tab2, tab3, tab4, tab_control)

        button_cart = ttk.Button(tab1, text="Add to cart", style='green.TButton', command=add_to_cart)
        button_cart.grid(row=r, column=0, columnspan=6, ipadx=265, ipady=10)

    # Display inventory status tab
    display_inventory(tab_control, tab1, tab2, tab3, tab4)


# Check if a product's items are in stock and return True or False
def check_stock_zero(number):
    inventory = pd.read_csv(INVENTORY_FILE)
    parts = pd.read_csv(PARTS_FILE)
    values = []

    for part in parts.index:
        # Find the component parts of the product, and check
        # if stock for each part is greater than 5 times quantity_per_product_unit (adding some buffer)
        if parts['product_id'][part] == number:
            min_number = float(parts['quantity_per_product_unit'][part]) * 5
            sku = parts['sku_id'][part]
            current_stock = float(inventory.query('sku_id==@sku').iloc[0]['current_stock'])
            values.append(current_stock > min_number)
    return values


# Display items added to cart, Confirm order button or cancel
def display_cart(items_ordered, tab1, tab2, tab3, tab4, tab_control):
    # Switch to second tab 'Active cart' on the screen
    tab_control.select(1)
    products = pd.read_csv(PRODUCTS_FILE)

    # Display header names
    header1 = ttk.Label(tab2, text='Product Name', font='-weight bold')
    header1.grid(row=0, column=0, columnspan=2, padx=50, pady=5)
    header2 = ttk.Label(tab2, text='Quantity Ordered', font='-weight bold')
    header2.grid(row=0, column=2, columnspan=2, padx=50, pady=5)
    header3 = ttk.Label(tab2, text='Sub-total', font='-weight bold')
    header3.grid(row=0, column=4, columnspan=2, padx=50, pady=5)

    r = 1

    # Display details of the line items of the current order
    for item in items_ordered:
        for line in products.index:
            if products['product_id'][line] == item['product_id']:
                name = products['product_name'][line]
                quantity = int(item['quantity_ordered'])
                value = float(products['price_per_unit'][line]) * quantity
                label1 = ttk.Label(tab2, text=name)
                label1.grid(row=r, column=0, columnspan=2, padx=5, pady=5)
                label2 = ttk.Label(tab2, text=quantity)
                label2.grid(row=r, column=2, columnspan=2, padx=5, pady=5)
                label3 = ttk.Label(tab2, text=value)
                label3.grid(row=r, column=4, columnspan=2, padx=5, pady=5)
                r += 1

    # Display summary of order
    summary_label1 = ttk.Label(tab2, text='Total', font='-weight bold')
    summary_label1.grid(row=r, column=0, columnspan=2, padx=5, pady=5)
    summary_label2 = ttk.Label(tab2, text=count_items(items_ordered), font='-weight bold')
    summary_label2.grid(row=r, column=2, columnspan=2, padx=5, pady=5)
    summary_label3 = ttk.Label(tab2, text=calculate_order_value(items_ordered), font='-weight bold')
    summary_label3.grid(row=r, column=4, columnspan=2, padx=5, pady=5)

    def cancel_order():
        items_ordered.clear()
        for widget in tab2.winfo_children():
            widget.destroy()
        tab_control.select(0)

    def confirm_order():
        # Create order ID and update items ordered list
        order_id = create_order_id(items_ordered)

        # Capture items ordered in a .csv file
        write_items_to_csv(items_ordered)

        # Capture the order summary in a .csv file
        record_order_summary(items_ordered, order_id)

        # Update stock
        update_stock_real_time(items_ordered)

        # Display order data
        display_order_data(tab3)

        # Display inventory
        display_inventory(tab_control, tab1, tab2, tab3, tab4)

        # Show success message to user
        messagebox.showinfo("Confirmation", "Thank you. The order has been confirmed.")

        # Clear items ordered list
        items_ordered.clear()
        for widget in tab2.winfo_children():
            widget.destroy()
        fill_tabs(tab_control, tab1, tab2, tab3, tab4)
        tab_control.select(0)

    button_cancel = ttk.Button(tab2, text="Cancel order", style='grey.TButton', command=cancel_order)
    button_cancel.grid(row=r + 1, column=0, columnspan=3, ipadx=50, ipady=10)
    button_confirm = ttk.Button(tab2, text="Confirm order", style='green.TButton', command=confirm_order)
    button_confirm.grid(row=r + 1, column=3, columnspan=3, ipadx=50, ipady=10)


# Count number of non-blank entries and return True if user has not entered any input
def check_for_blank_entries(entries):
    count = 0

    for entry in entries:
        if entry.get() != '':
            count += 1
    if count == 0:
        return True
    else:
        return False


# Go through the user entries one by one, return the list of items ordered and record it in a csv
def list_items_ordered(entries, items_ordered):
    entry_num = 1
    for entry in entries:
        if entry.get() == '':
            entry_num += 1
        else:
            item_entry = {'product_id': entry_num, 'quantity_ordered': entry.get()}
            items_ordered.append(item_entry)
            entry_num += 1


# Checks last order number stored, increases order number by 1 and returns an Order ID
def create_order_id(items_ordered):
    with open(ORDER_DATA, 'r', encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter=',')
        past_order_ids = []

        for row in reader:
            past_order_ids.append(row[0])

        if len(past_order_ids) == 0:
            global order_number
            order_number += 1
            order_id = pad(order_number, 6)
            for item in items_ordered:
                item['order_id'] = order_number
            return order_id
        else:
            order_number = int(past_order_ids[-1]) + 1
            order_id = pad(order_number, 6)
            for item in items_ordered:
                item['order_id'] = order_number
            return order_id


# Adds 0s to the str version of a number till the length of the string is less than goal length
def pad(number, goal_length):
    number_string = str(number)
    while len(number_string) < goal_length:
        number_string = '0' + number_string
    return number_string


# Capture items ordered real time in a .csv file post confirmation of an order
def write_items_to_csv(items_ordered):
    with open(ITEMS_DATA, 'a', newline='') as file:
        fieldnames = ['order_id', 'product_id', 'quantity_ordered']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        for item in items_ordered:
            writer.writerow(item)


# Capture order summary real time in a .csv file post confirmation of an order
def record_order_summary(items_ordered, order_id):
    order_dict = {
        'order_id': order_id,
        'count_of_items': count_items(items_ordered),
        'order_value': calculate_order_value(items_ordered),
        'date': date.today(),
        'timestamp': dt.now()
    }

    with open(ORDER_DATA, 'a', newline='') as file:
        fieldnames = ['order_id', 'count_of_items', 'order_value', 'date', 'timestamp']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(order_dict)


# Calculate total count of items in an order
def count_items(items_ordered):
    count = 0

    for item in items_ordered:
        count += int(item['quantity_ordered'])

    return count


# Calculate order value of a particular order
def calculate_order_value(items_ordered):
    product_catalogue = upload_unique_entries(PRODUCTS_FILE)
    order_value = 0

    for item in items_ordered:
        for product in product_catalogue:
            if item['product_id'] == int(product['product_id']):
                order_value += int(item['quantity_ordered']) * float(product['price_per_unit'])

    return order_value


# Parse through items ordered and reduce the quantity of component parts from the inventory file
def update_stock_real_time(items_ordered):
    inventory = pd.read_csv(INVENTORY_FILE)
    parts = pd.read_csv(PARTS_FILE)

    for item in items_ordered:
        for part in parts.index:
            # Find the component parts of each item ordered, calculate quantity ordered and update stock
            if parts['product_id'][part] == item['product_id']:
                delta_stock = float(parts['quantity_per_product_unit'][part]) * float(item['quantity_ordered'])
                sku = parts['sku_id'][part]
                previous_stock = float(inventory.query('sku_id==@sku').iloc[0]['current_stock'])
                updated_stock = previous_stock - delta_stock
                for stock in inventory.index:
                    if inventory['sku_id'][stock] == sku:
                        r = inventory[inventory['sku_id'] == sku].index.item()
                        if updated_stock > 0:
                            inventory.at[r, 'current_stock'] = updated_stock
                        else:
                            inventory.at[r, 'current_stock'] = 0
                        inventory.at[r, 'last_update'] = dt.now()
                        inventory.to_csv(INVENTORY_FILE, index=False)


# Compute order summary and display on the 'Past Orders' tab
# TODO: This is super inefficient code. Need to make it update real-time + loop to display.
def display_order_data(tab3):
    orders = pd.read_csv(ORDER_DATA)

    order_vol_today = 0
    items_ordered_today = 0
    order_val_today = 0
    order_vol_this_week = 0
    items_ordered_week = 0
    order_val_this_week = 0
    order_vol_this_month = 0
    items_ordered_month = 0
    order_val_this_month = 0

    for x in orders.index:
        date_time_str = orders['timestamp'][x]
        date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        if date_time_obj.date().day == date.today().day:
            order_vol_today += 1
            items_ordered_today += orders['count_of_items'][x]
            order_val_today += orders['order_value'][x]
            if date_time_obj.date().isocalendar()[1] == date.today().isocalendar()[1]:
                order_vol_this_week += 1
                items_ordered_week += orders['count_of_items'][x]
                order_val_this_week += orders['order_value'][x]
                if date_time_obj.date().month == date.today().month:
                    order_vol_this_month += 1
                    items_ordered_month += orders['count_of_items'][x]
                    order_val_this_month += orders['order_value'][x]

    header_1 = ttk.Label(tab3, text='Order Count', font='-weight bold')
    header_1.grid(row=0, column=1, padx=5, pady=5)
    header_2 = ttk.Label(tab3, text='Items Ordered', font='-weight bold')
    header_2.grid(row=0, column=2, padx=5, pady=5)
    header_3 = ttk.Label(tab3, text='Order value', font='-weight bold')
    header_3.grid(row=0, column=3, padx=5, pady=5)
    header_4 = ttk.Label(tab3, text='Items / order', font='-weight bold')
    header_4.grid(row=0, column=4, padx=5, pady=5)
    header_5 = ttk.Label(tab3, text='Avg. value / order', font='-weight bold')
    header_5.grid(row=0, column=5, padx=5, pady=5)

    row_h1 = ttk.Label(tab3, text='Today', font='-weight bold')
    row_h1.grid(row=1, column=0, padx=5, pady=5)
    row_h2 = ttk.Label(tab3, text='This week', font='-weight bold')
    row_h2.grid(row=2, column=0, padx=5, pady=5)
    row_h3 = ttk.Label(tab3, text='This month', font='-weight bold')
    row_h3.grid(row=3, column=0, padx=5, pady=5)

    label_1x1 = ttk.Label(tab3, text=str(order_vol_today))
    label_1x1.grid(row=1, column=1, padx=5, pady=5)
    label_1x2 = ttk.Label(tab3, text=str(items_ordered_today))
    label_1x2.grid(row=1, column=2, padx=5, pady=5)
    label_1x3 = ttk.Label(tab3, text="{:.1f}".format(order_val_today))
    label_1x3.grid(row=1, column=3, padx=5, pady=5)
    label_1x4 = ttk.Label(tab3, text="{:.1f}".format(round(items_ordered_today / order_vol_today, 2)))
    label_1x4.grid(row=1, column=4, padx=5, pady=5)
    label_1x5 = ttk.Label(tab3, text="{:.1f}".format(round(order_val_today / order_vol_today, 2)))
    label_1x5.grid(row=1, column=5, padx=5, pady=5)

    label_2x1 = ttk.Label(tab3, text=str(order_vol_this_week))
    label_2x1.grid(row=2, column=1, padx=5, pady=5)
    label_2x2 = ttk.Label(tab3, text=str(items_ordered_week))
    label_2x2.grid(row=2, column=2, padx=5, pady=5)
    label_2x3 = ttk.Label(tab3, text="{:.1f}".format(order_val_this_week))
    label_2x3.grid(row=2, column=3, padx=5, pady=5)
    label_2x4 = ttk.Label(tab3, text="{:.1f}".format(round(items_ordered_week / order_vol_this_week, 2)))
    label_2x4.grid(row=2, column=4, padx=5, pady=5)
    label_2x5 = ttk.Label(tab3, text="{:.1f}".format(round(order_val_this_week / order_vol_this_week, 2)))
    label_2x5.grid(row=2, column=5, padx=5, pady=5)

    label_3x1 = ttk.Label(tab3, text=str(order_vol_this_month))
    label_3x1.grid(row=3, column=1, padx=5, pady=5)
    label_3x2 = ttk.Label(tab3, text=str(items_ordered_month))
    label_3x2.grid(row=3, column=2, padx=5, pady=5)
    label_3x3 = ttk.Label(tab3, text="{:.1f}".format(order_val_this_month))
    label_3x3.grid(row=3, column=3, padx=5, pady=5)
    label_3x4 = ttk.Label(tab3, text="{:.1f}".format(round(items_ordered_month / order_vol_this_month, 2)))
    label_3x4.grid(row=3, column=4, padx=5, pady=5)
    label_3x5 = ttk.Label(tab3, text="{:.1f}".format(round(order_val_this_month / order_vol_this_month, 2)))
    label_3x5.grid(row=3, column=5, padx=5, pady=5)

    return


# Display current inventory status and show basic alerts when stock is less than threshold
# TODO: Need to figure a less messy way to display and update a csv :)
def display_inventory(tab_control, tab1, tab2, tab3, tab4):
    for widget in tab4.winfo_children():
        widget.destroy()

    replenish_list = []

    # Print header row of inventory file
    with open(INVENTORY_FILE, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        c = 0
        for x in reader.fieldnames[1:]:
            header = ttk.Label(tab4, text=x, font='-weight bold')
            header.grid(row=0, column=c, padx=5, pady=5)
            c += 1
        header = ttk.Label(tab4, text='action', font='-weight bold')
        header.grid(row=0, column=c, padx=5, pady=5)

        r = 1

    # Display each cell value and show timestamp is a more friendly format
    with open(INVENTORY_FILE, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        for line in reader:
            c = 0
            for elem in line[1:5]:
                stock_items = ttk.Label(tab4, text=elem)
                stock_items.grid(row=r, column=c, padx=5, pady=5)
                c += 1
            date_time_str = line[5]
            date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
            new_date_time_str = date_time_obj.strftime("%d %b %H:%M")
            stock_items = ttk.Label(tab4, text=new_date_time_str)
            stock_items.grid(row=r, column=c, padx=5, pady=5)
            c += 1

            # Check stock count against threshold and display if all is good or if a user needs to replenish something
            if int(line[4]) > int(line[2]):
                action = ttk.Label(tab4, text='all good', foreground='green')
                action.grid(row=r, column=c, padx=5, pady=5)
            else:
                action = ttk.Label(tab4, text='replenish', foreground='red')
                action.grid(row=r, column=c, padx=5, pady=5)
                replenish_list.append(r)
            r += 1

        # Depending on the items list to replenish, increase stock count by two times the minimum threshold value
        def replenish_now(rep_list):
            inventory = pd.read_csv(INVENTORY_FILE)

            for item in rep_list:
                for stock in inventory.index:
                    s1 = int(inventory['sku_id'][stock])
                    s2 = int(inventory['sku_id'][item - 1])
                    if s1 == s2:
                        var = inventory[inventory['sku_id'] == inventory['sku_id'][stock]].index.item()
                        current_stock = inventory['current_stock'][stock]
                        replenish_amount = 2 * inventory['min_stock'][stock]
                        inventory.at[var, 'current_stock'] = current_stock + replenish_amount
                        inventory.at[var, 'last_update'] = dt.now()
                        inventory.to_csv(INVENTORY_FILE, index=False)

            # Update the counts on the display tab
            display_inventory(tab_control, tab1, tab2, tab3, tab4)

            fill_tabs(tab_control, tab1, tab2, tab3, tab4)

            return

        def take_more_orders():
            tab_control.select(0)

        if len(replenish_list) > 0:
            button = ttk.Button(tab4, text='replenish now', style='red.TButton',
                                command=lambda: replenish_now(replenish_list))
            button.grid(row=r, column=0, columnspan=6, ipadx=265, ipady=10)
        else:
            button = ttk.Button(tab4, text='Take more orders!', style='green.TButton',
                                command=take_more_orders)
            button.grid(row=r, column=0, columnspan=6, ipadx=250, ipady=10)

    return


# Take user input in the form of a csv file to build a dictionary
def upload_unique_entries(filename):
    with open(filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        dict_list = []
        for row in reader:
            dict_list.append(row)

    return dict_list


if __name__ == "__main__":
    main()
