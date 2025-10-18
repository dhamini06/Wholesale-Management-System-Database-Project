import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Database setup
conn = sqlite3.connect('wholesale.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                price REAL,
                quantity INTEGER
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                contact TEXT
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                total REAL,
                date TEXT
            )''')
conn.commit()

st.title("🏢 Wholesale Management System")

menu = ["Manage Products", "Manage Suppliers", "Create Order", "View Records"]
choice = st.sidebar.selectbox("Menu", menu)

# Manage Products
if choice == "Manage Products":
    st.subheader("📦 Manage Products")
    action = st.radio("Action", ["Add Product", "View Products"])
    if action == "Add Product":
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0.0)
        quantity = st.number_input("Quantity", min_value=0)
        if st.button("Add Product"):
            c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", 
                      (name, price, quantity))
            conn.commit()
            st.success(f"Product '{name}' added successfully!")
    elif action == "View Products":
        products_df = pd.read_sql("SELECT * FROM products", conn)
        st.dataframe(products_df)

# Manage Suppliers
elif choice == "Manage Suppliers":
    st.subheader("🤝 Manage Suppliers")
    action = st.radio("Action", ["Add Supplier", "View Suppliers"])
    if action == "Add Supplier":
        name = st.text_input("Supplier Name")
        contact = st.text_input("Contact Info")
        if st.button("Add Supplier"):
            c.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
            conn.commit()
            st.success(f"Supplier '{name}' added successfully!")
    elif action == "View Suppliers":
        suppliers_df = pd.read_sql("SELECT * FROM suppliers", conn)
        st.dataframe(suppliers_df)

# Create Orders
elif choice == "Create Order":
    st.subheader("📝 Create Order")
    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
    products = pd.read_sql("SELECT * FROM products", conn)
    if suppliers.empty or products.empty:
        st.warning("Please add suppliers and products first!")
    else:
        supplier_id = st.selectbox("Select Supplier", suppliers['id'])
        product_id = st.selectbox("Select Product", products['id'])
        quantity = st.number_input("Quantity", min_value=1)
        product_price = products.loc[products['id']==product_id, 'price'].values[0]
        total = quantity * product_price
        if st.button("Place Order"):
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO orders (supplier_id, product_id, quantity, total, date) VALUES (?, ?, ?, ?, ?)",
                      (supplier_id, product_id, quantity, total, date))
            # Update product quantity
            c.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, product_id))
            conn.commit()
            st.success(f"Order placed! Total: ₹{total:.2f}")

# View Records
elif choice == "View Records":
    st.subheader("📂 All Records")
    
    st.write("**Products**")
    products_df = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(products_df)
    
    st.write("**Suppliers**")
    suppliers_df = pd.read_sql("SELECT * FROM suppliers", conn)
    st.dataframe(suppliers_df)
    
    st.write("**Orders**")
    orders_df = pd.read_sql("SELECT * FROM orders", conn)
    st.dataframe(orders_df)

conn.close()
