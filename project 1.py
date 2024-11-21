import sqlite3
import csv
from datetime import datetime
import random
from tabulate import tabulate
import os

# Connect to the database
con = sqlite3.connect('superstore.db')
cur = con.cursor()

# Check if the table exists, and create it if it doesn't
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
if not cur.fetchone():
    # Create Products table
    cur.execute("""
    CREATE TABLE products(
        product_id VARCHAR(20) PRIMARY KEY,
        category VARCHAR(20),
        sub_category VARCHAR(20),
        product_name VARCHAR(100),
        unit_price FLOAT
    )""")
    print('Products table created')

    # Insert predefined products
    products_data = [
        ('PROD-001', 'Furniture', 'Chairs', 'Executive Leather Chair', 299.99),
        ('PROD-002', 'Furniture', 'Tables', 'L-Shape Office Desk', 449.99),
        ('PROD-003', 'Furniture', 'Chairs', 'Ergonomic Mesh Chair', 189.99),
        ('PROD-004', 'Furniture', 'Tables', 'Conference Table', 799.99),
        ('PROD-005', 'Furniture', 'Storage', 'Bookshelf', 159.99),
        ('PROD-006', 'Office Supplies', 'Storage', 'File Cabinet', 129.99),
        ('PROD-007', 'Office Supplies', 'Paper', 'Printer Paper Box', 45.99),
        ('PROD-008', 'Office Supplies', 'Binders', 'Heavy Duty Binder', 18.99),
        ('PROD-009', 'Office Supplies', 'Supplies', 'Stapler Set', 12.99),
        ('PROD-010', 'Office Supplies', 'Art', 'Whiteboard', 89.99),
        ('PROD-011', 'Technology', 'Phones', 'VoIP Phone System', 299.99),
        ('PROD-012', 'Technology', 'Accessories', 'Wireless Mouse', 29.99),
        ('PROD-013', 'Technology', 'Machines', 'Color Laser Printer', 499.99),
        ('PROD-014', 'Technology', 'Copiers', 'Heavy Duty Copier', 1299.99),
        ('PROD-015', 'Technology', 'Accessories', 'Mechanical Keyboard', 89.99),
    ]
    cur.executemany("INSERT INTO products VALUES(?, ?, ?, ?, ?)", products_data)

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers';")
if not cur.fetchone():
    # Create Customers table
    cur.execute("""
    CREATE TABLE customers(
        customer_id VARCHAR(20) PRIMARY KEY,
        customer_name VARCHAR(50),
        segment VARCHAR(20),
        country VARCHAR(50),
        city VARCHAR(50),
        state VARCHAR(50),
        postal_code VARCHAR(10),
        region VARCHAR(20)
    )""")
    print('Customers table created')

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='orders';")
if not cur.fetchone():
    # Create Orders table with foreign keys
    cur.execute("""
    CREATE TABLE orders(
        order_id VARCHAR(20) PRIMARY KEY,
        order_date DATE,
        ship_date DATE,
        ship_mode VARCHAR(20),
        customer_id VARCHAR(20),
        product_id VARCHAR(20),
        quantity INT,
        discount FLOAT,
        sales FLOAT,
        profit FLOAT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )""")
    print('Orders table created')

con.commit()

# Add these constants at the beginning of the file, after the imports
SHIP_MODES = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
SEGMENTS = ['Consumer', 'Corporate', 'Home Office']
REGIONS = ['North', 'South', 'East', 'West']
CATEGORIES = {
    'Furniture': ['Bookcases', 'Chairs', 'Furnishings', 'Tables'],
    'Office Supplies': ['Appliances', 'Art', 'Binders', 'Envelopes', 'Fasteners', 'Labels', 'Paper', 'Storage', 'Supplies'],
    'Technology': ['Accessories', 'Copiers', 'Machines', 'Phones']
}

# Modified insert_record function for superstore
def calculate_financials(quantity, unit_price):
    """Calculate discount, sales and profit based on quantity and price"""
    
    # Discount calculation based on quantity
    if quantity >= 50:
        discount = 0.20  # 20% discount for bulk orders (50+ units)
    elif quantity >= 20:
        discount = 0.15  # 15% discount for medium orders (20-49 units)
    elif quantity >= 10:
        discount = 0.10  # 10% discount for small bulk orders (10-19 units)
    elif quantity >= 5:
        discount = 0.05  # 5% discount for multiple units (5-9 units)
    else:
        discount = 0.00  # No discount for small quantities
    
    # Calculate sales (price after discount)
    subtotal = quantity * unit_price
    discount_amount = subtotal * discount
    sales = subtotal - discount_amount
    
    # Calculate profit based on product category
    # Different profit margins for different price ranges
    if unit_price >= 500:
        profit_margin = 0.25  # 25% profit margin for high-end items
    elif unit_price >= 100:
        profit_margin = 0.30  # 30% profit margin for mid-range items
    else:
        profit_margin = 0.35  # 35% profit margin for low-cost items
    
    profit = sales * profit_margin
    
    return round(discount, 2), round(sales, 2), round(profit, 2)

def insert_record():
    try:
        # First, insert or select customer
        print("\nCustomer Details:")
        customer_id = input("Enter Customer ID: ")
        cur.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        customer = cur.fetchone()
        
        if not customer:
            # Insert new customer
            customer_name = input("Enter Customer Name: ")
            print("\nAvailable Segments:")
            for i, seg in enumerate(SEGMENTS, 1):
                print(f"{i}. {seg}")
            segment_choice = int(input("Choose Segment (enter number): "))
            segment = SEGMENTS[segment_choice-1]
            
            country = input("Enter Country: ")
            city = input("Enter City: ")
            state = input("Enter State: ")
            postal_code = input("Enter Postal Code: ")
            
            print("\nAvailable Regions:")
            for i, reg in enumerate(REGIONS, 1):
                print(f"{i}. {reg}")
            region_choice = int(input("Choose Region (enter number): "))
            region = REGIONS[region_choice-1]
            
            cur.execute("""
            INSERT INTO customers VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, customer_name, segment, country, city, state, postal_code, region))
            print("New customer added successfully!")

        # Show available products
        print("\nAvailable Products:")
        cur.execute("SELECT product_id, product_name, category, unit_price FROM products")
        products = cur.fetchall()
        for prod in products:
            print(f"ID: {prod[0]}, Name: {prod[1]}, Category: {prod[2]}, Price: ${prod[3]:.2f}")
        
        # Get order details
        order_id = input("\nEnter Order ID: ")
        order_date = input("Enter Order Date (YYYY-MM-DD): ")
        ship_date = input("Enter Ship Date (YYYY-MM-DD): ")
        
        print("\nAvailable Ship Modes:")
        for i, mode in enumerate(SHIP_MODES, 1):
            print(f"{i}. {mode}")
        ship_choice = int(input("Choose Ship Mode (enter number): "))
        ship_mode = SHIP_MODES[ship_choice-1]
        
        product_id = input("Enter Product ID from the list above: ")
        quantity = int(input("Enter Quantity: "))
        
        # Get product price
        cur.execute("SELECT unit_price FROM products WHERE product_id = ?", (product_id,))
        unit_price = cur.fetchone()[0]
        
        # Calculate financials
        discount, sales, profit = calculate_financials(quantity, unit_price)
        
        # Insert order
        cur.execute("""
        INSERT INTO orders VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, order_date, ship_date, ship_mode, customer_id, product_id, 
              quantity, discount, sales, profit))
        
        print(f"""
Order Summary:
-------------
Order ID: {order_id}
Quantity: {quantity}
Unit Price: ${unit_price:.2f}
Subtotal: ${(quantity * unit_price):.2f}
Discount: {discount:.2%}
Discount Amount: ${(quantity * unit_price * discount):.2f}
Final Sales: ${sales:.2f}
Profit: ${profit:.2f}
""")
        con.commit()
        
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            print("Error: Invalid Customer ID or Product ID")
        else:
            print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Modified show_records function
def show_records():
    while True:
        print("\nWhich table would you like to view?")
        print("1. Orders (with full details)")
        print("2. Customers")
        print("3. Products")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ")
        
        try:
            if choice == '1':
                # Show orders with joined details
                cur.execute('''
                SELECT o.order_id, o.order_date, o.ship_date, o.ship_mode,
                       c.customer_name, c.segment, c.country, c.city, c.state,
                       p.product_name, p.category, p.sub_category,
                       o.quantity, o.discount, o.sales, o.profit
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN products p ON o.product_id = p.product_id
                ''')
                records = cur.fetchall()
                
                if records:
                    headers = ['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 
                             'Customer', 'Segment', 'Country', 'City', 'State',
                             'Product', 'Category', 'Sub-Category',
                             'Quantity', 'Discount', 'Sales', 'Profit']
                    
                    formatted_records = []
                    for record in records:
                        formatted_record = list(record)
                        formatted_record[13] = f"{record[13]:.2%}"  # Discount
                        formatted_record[14] = f"${record[14]:.2f}"  # Sales
                        formatted_record[15] = f"${record[15]:.2f}"  # Profit
                        formatted_records.append(formatted_record)
                    
                    print("\nOrders with Details:")
                    print(tabulate(formatted_records, headers=headers, tablefmt='grid'))
                    print(f"\nTotal Orders: {len(records)}")
                else:
                    print("No orders found.")
                    
            elif choice == '2':
                # Show customers table
                cur.execute('SELECT * FROM customers')
                records = cur.fetchall()
                
                if records:
                    headers = ['Customer ID', 'Customer Name', 'Segment', 'Country', 
                             'City', 'State', 'Postal Code', 'Region']
                    print("\nCustomers:")
                    print(tabulate(records, headers=headers, tablefmt='grid'))
                    print(f"\nTotal Customers: {len(records)}")
                else:
                    print("No customers found.")
                    
            elif choice == '3':
                # Show products table
                cur.execute('SELECT * FROM products')
                records = cur.fetchall()
                
                if records:
                    headers = ['Product ID', 'Category', 'Sub-Category', 
                             'Product Name', 'Unit Price']
                    
                    formatted_records = []
                    for record in records:
                        formatted_record = list(record)
                        formatted_record[4] = f"${record[4]:.2f}"  # Format unit price
                        formatted_records.append(formatted_record)
                    
                    print("\nProducts:")
                    print(tabulate(formatted_records, headers=headers, tablefmt='grid'))
                    print(f"\nTotal Products: {len(records)}")
                else:
                    print("No products found.")
                    
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")

# Add new function to download as CSV
def download_as_csv():
    try:
        print("\nWhich data would you like to export?")
        print("1. Orders (with full details)")
        print("2. Customers")
        print("3. Products")
        choice = input("Enter your choice: ")
        
        # Create descriptive filename based on choice
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if choice == '1':
            filename = f"superstore_orders_{timestamp}.csv"
        elif choice == '2':
            filename = f"superstore_customers_{timestamp}.csv"
        elif choice == '3':
            filename = f"superstore_products_{timestamp}.csv"
        else:
            print("Invalid choice")
            return
            
        full_path = os.path.abspath(filename)
        
        if choice == '1':
            # Export orders with full details
            cur.execute('''
            SELECT o.order_id, o.order_date, o.ship_date, o.ship_mode,
                   c.customer_name, c.segment, c.country, c.city, c.state,
                   p.product_name, p.category, p.sub_category,
                   o.quantity, o.discount, o.sales, o.profit
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            JOIN products p ON o.product_id = p.product_id
            ''')
            headers = ['Order ID', 'Order Date', 'Ship Date', 'Ship Mode', 
                      'Customer', 'Segment', 'Country', 'City', 'State',
                      'Product', 'Category', 'Sub-Category',
                      'Quantity', 'Discount', 'Sales', 'Profit']
        
        elif choice == '2':
            # Export customers
            cur.execute('SELECT * FROM customers')
            headers = ['Customer ID', 'Customer Name', 'Segment', 'Country', 
                      'City', 'State', 'Postal Code', 'Region']
        
        elif choice == '3':
            # Export products
            cur.execute('SELECT * FROM products')
            headers = ['Product ID', 'Category', 'Sub-Category', 
                      'Product Name', 'Unit Price']
            
        rows = cur.fetchall()
        if not rows:
            print("No data to export.")
            return
            
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"Data successfully exported to {filename}")
        print(f"Full path: {full_path}")
    
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")

# Add these functions before the main menu loop:

def update_table():
    while True:
        print("\n1. Update Order Details \n2. Update Customer Details \n3. Update Product Details")
        print("4. Update Sales Details \n5. Exit")
        choice = int(input("Enter your choice: "))

        try:
            if choice in [1, 2, 3, 4]:
                order_id = input("Enter Order ID of the record to update: ")
                
            if choice == 1:
                print("\n1. Ship Mode \n2. Order Date \n3. Ship Date")
                field_choice = int(input("Enter field to update: "))
                if field_choice == 1:
                    new_value = input("Enter new Ship Mode: ")
                    cur.execute("UPDATE superstore SET ship_mode = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 2:
                    new_value = input("Enter new Order Date (YYYY-MM-DD): ")
                    cur.execute("UPDATE superstore SET order_date = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 3:
                    new_value = input("Enter new Ship Date (YYYY-MM-DD): ")
                    cur.execute("UPDATE superstore SET ship_date = ? WHERE order_id = ?", (new_value, order_id))
                
            elif choice == 2:
                print("\n1. Customer Name \n2. Segment \n3. Country \n4. City \n5. State")
                print("6. Postal Code \n7. Region")
                field_choice = int(input("Enter field to update: "))
                if field_choice == 1:
                    new_value = input("Enter new Customer Name: ")
                    cur.execute("UPDATE superstore SET customer_name = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 2:
                    new_value = input("Enter new Segment: ")
                    cur.execute("UPDATE superstore SET segment = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 3:
                    new_value = input("Enter new Country: ")
                    cur.execute("UPDATE superstore SET country = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 4:
                    new_value = input("Enter new City: ")
                    cur.execute("UPDATE superstore SET city = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 5:
                    new_value = input("Enter new State: ")
                    cur.execute("UPDATE superstore SET state = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 6:
                    new_value = input("Enter new Postal Code: ")
                    cur.execute("UPDATE superstore SET postal_code = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 7:
                    new_value = input("Enter new Region: ")
                    cur.execute("UPDATE superstore SET region = ? WHERE order_id = ?", (new_value, order_id))
                
            elif choice == 3:
                print("\n1. Product ID \n2. Category and Sub-Category \n3. Product Name")
                field_choice = int(input("Enter field to update: "))
                if field_choice == 1:
                    new_value = input("Enter new Product ID: ")
                    cur.execute("UPDATE superstore SET product_id = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 2:
                    # Show category options
                    print("\nAvailable Categories:")
                    for i, cat in enumerate(CATEGORIES.keys(), 1):
                        print(f"{i}. {cat}")
                    cat_choice = int(input("Choose Category (enter number): "))
                    category = list(CATEGORIES.keys())[cat_choice-1]
                    
                    # Show sub-category options
                    print(f"\nAvailable Sub-Categories for {category}:")
                    sub_cats = CATEGORIES[category]
                    for i, sub in enumerate(sub_cats, 1):
                        print(f"{i}. {sub}")
                    sub_choice = int(input("Choose Sub-Category (enter number): "))
                    sub_category = sub_cats[sub_choice-1]
                    
                    cur.execute("""
                        UPDATE superstore 
                        SET category = ?, sub_category = ? 
                        WHERE order_id = ?
                        """, (category, sub_category, order_id))
                elif field_choice == 3:
                    new_value = input("Enter new Product Name: ")
                    cur.execute("UPDATE superstore SET product_name = ? WHERE order_id = ?", (new_value, order_id))
                
            elif choice == 4:
                print("\n1. Quantity \n2. Discount \n3. Sales \n4. Profit")
                field_choice = int(input("Enter field to update: "))
                if field_choice == 1:
                    new_value = int(input("Enter new Quantity: "))
                    cur.execute("UPDATE superstore SET quantity = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 2:
                    new_value = float(input("Enter new Discount: "))
                    cur.execute("UPDATE superstore SET discount = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 3:
                    new_value = float(input("Enter new Sales: "))
                    cur.execute("UPDATE superstore SET sales = ? WHERE order_id = ?", (new_value, order_id))
                elif field_choice == 4:
                    new_value = float(input("Enter new Profit: "))
                    cur.execute("UPDATE superstore SET profit = ? WHERE order_id = ?", (new_value, order_id))
                
            elif choice == 5:
                print("Exiting update menu.")
                break
            
            con.commit()
            print("Record updated successfully!")
            
        except ValueError:
            print("Invalid input! Please enter correct values.")
        except sqlite3.Error as e:
            print(f"Database error: {e}")

def delete_records():
    while True:
        print("\n1. Delete by Order ID")
        print("2. Delete by Customer ID (will delete all related orders)")
        print("3. Delete by Product ID (will delete all related orders)")
        print("4. Exit")
        choice = input("Enter your choice: ")

        try:
            if choice == '1':
                order_id = input("Enter the Order ID to delete: ")
                cur.execute("DELETE FROM orders WHERE order_id = ?", (order_id,))
                if cur.rowcount > 0:
                    print(f"Order {order_id} deleted successfully")
                else:
                    print("Order not found")

            elif choice == '2':
                customer_id = input("Enter the Customer ID: ")
                cur.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,))
                order_count = cur.fetchone()[0]
                if order_count > 0:
                    confirm = input(f"This will delete {order_count} orders. Continue? (y/n): ")
                    if confirm.lower() == 'y':
                        cur.execute("DELETE FROM orders WHERE customer_id = ?", (customer_id,))
                        cur.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                        print(f"Customer and {order_count} orders deleted")
                else:
                    cur.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                    print("Customer deleted")

            elif choice == '3':
                product_id = input("Enter the Product ID: ")
                cur.execute("SELECT COUNT(*) FROM orders WHERE product_id = ?", (product_id,))
                order_count = cur.fetchone()[0]
                if order_count > 0:
                    confirm = input(f"This will delete {order_count} orders. Continue? (y/n): ")
                    if confirm.lower() == 'y':
                        cur.execute("DELETE FROM orders WHERE product_id = ?", (product_id,))
                        cur.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                        print(f"Product and {order_count} orders deleted")
                else:
                    cur.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
                    print("Product deleted")

            elif choice == '4':
                break

            con.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")

def alter_table():
    while True:
        print("\nWhich table would you like to alter?")
        print("1. Orders")
        print("2. Customers")
        print("3. Products")
        print("4. Back to main menu")
        
        table_choice = input("Enter your choice: ")
        
        if table_choice == '4':
            break
            
        if table_choice not in ['1', '2', '3']:
            print("Invalid choice. Please try again.")
            continue
            
        table_name = {
            '1': 'orders',
            '2': 'customers',
            '3': 'products'
        }[table_choice]
        
        print(f"\nAltering {table_name} table:")
        print("1. Add Column")
        print("2. Rename Column")
        print("3. Rename Table")
        print("4. Back to table selection")
        
        try:
            choice = int(input("Enter your choice: "))
            
            if choice == 1:
                colname = input("Enter the new column name: ")
                datatype = input("Enter the data type for the new column: ")
                cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {colname} {datatype}")
                print(f"Column '{colname}' successfully added to {table_name} table.")

            elif choice == 2:
                oldcol = input("Enter the current column name: ")
                newcol = input("Enter the new column name: ")
                cur.execute(f"ALTER TABLE {table_name} RENAME COLUMN {oldcol} TO {newcol}")
                print(f"Column renamed from '{oldcol}' to '{newcol}' in {table_name} table")

            elif choice == 3:
                newtable = input("Enter the new table name: ")
                cur.execute(f"ALTER TABLE {table_name} RENAME TO {newtable}")
                print(f"Table '{table_name}' renamed to '{newtable}'")

            elif choice == 4:
                continue

            con.commit()

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def describe():
    while True:
        print("\nWhich table would you like to describe?")
        print("1. Orders")
        print("2. Customers")
        print("3. Products")
        print("4. Back to main menu")
        
        choice = input("Enter your choice: ")
        
        if choice == '4':
            break
            
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Please try again.")
            continue
            
        table_name = {
            '1': 'orders',
            '2': 'customers',
            '3': 'products'
        }[choice]
        
        try:
            cur.execute(f"PRAGMA table_info({table_name})")
            columns = cur.fetchall()
            
            if columns:
                print(f"\n{table_name.title()} Table Structure:")
                print("-" * 80)
                print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Primary Key':<12}")
                print("-" * 80)
                
                for col in columns:
                    name = col[1]
                    data_type = col[2]
                    nullable = "No" if col[3] else "Yes"
                    pk = "Yes" if col[5] else "No"
                    print(f"{name:<20} {data_type:<15} {nullable:<10} {pk:<12}")
            else:
                print(f"No table named '{table_name}' found.")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")

# Modify the main menu to remove truncate and drop table options
while True:
    print("\n1. Show Records \n2. Insert Records \n3. Update Records \n4. Delete Records")
    print("5. Alter Table \n6. Describe Table \n7. Download as CSV \n8. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        show_records()
    elif choice == '2':
        insert_record()
    elif choice == '3':
        update_table()
    elif choice == '4':
        delete_records()
    elif choice == '5':
        alter_table()
    elif choice == '6':
        describe()
    elif choice == '7':
        download_as_csv()
    elif choice == '8':
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please choose again.")

# Close the connection
con.close()

