

import streamlit as st
import pandas as pd
import os
from datetime import date
from io import BytesIO

#Constants
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ITEMS = [
    "TUSKER", "PILISNER", "TUSKER MALT", "TUSKER LITE", "GUINESS KUBWA", "GUINESS SMALL", "BALOZICAN",
    "WHITE CAP", "BALOZI", "SMIRNOFFICE", "SAVANNAH", "SNAPP", "TUSKER CIDER", "KINGFISHER", "ALLSOPPS",
    "G.K CAN", "T.LITE CAN", "GUARANA", "REDBULL", "RICHOT ½", "RICHOT ¼", "VICEROY ½", "VICEROY ¼",
    "VODKA½", "VODKA¼", "KENYACANE ¾", "KENYACANE ½", "KENYACANE ¼", "GILBEYS ½", "GILBEYS ¼", "V&A 750ml",
    "CHROME", "TRIPLE ACE", "BLACK AND WHITE", "KIBAO½", "KIBAO¼", "HUNTERS ½", "HUNTERS ¼", "CAPTAIN MORGAN",
    "KONYAGI", "V&A", "COUNTY", "BEST 750ml", "WATER 1L", "WATER½", "LEMONADE", "CAPRICE", "FAXE", "C.MORGAN",
    "VAT 69", "SODA300ML", "SODA500ML", "BLACK AND WHITE", "BEST", "CHROME 750ml", "MANGO", "TRUST", "PUNCH",
    "VODKA 750ml", "KONYAGI 500ml", "GILBEYS 750m"
]

#Helper Functions

def get_price_file():
    return os.path.join(DATA_DIR, "item_prices.csv")

def load_prices():
    price_file = get_price_file()
    if os.path.exists(price_file):
        df = pd.read_csv(price_file, index_col=0)
        prices = df["Price"].to_dict()
    else:
        prices = {item: 0.0 for item in ITEMS}
    return prices

def save_prices(prices):
    df = pd.DataFrame.from_dict(prices, orient="index", columns=["Price"])
    df.to_csv(get_price_file())

def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in df_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    processed_data = output.getvalue()
    return processed_data

def load_report(date_str):
    file_path = os.path.join(DATA_DIR, f"{date_str}.xlsx")
    if os.path.exists(file_path):
        xls = pd.ExcelFile(file_path)
        data = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
        return data
    else:
        return None

def list_saved_reports():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".xlsx")]
    dates = [f.replace(".xlsx", "") for f in files]
    return sorted(dates, reverse=True)

#Streamlit App 

st.set_page_config(page_title="Pillars Bar Management App", layout="wide")
st.title("Pillars Bar & Accommodation Management")

#Sidebar for Navigation 
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose the app mode", ["Data Entry", "View Past Reports"])

if app_mode == "Data Entry":
    # --- Date Selection ---
    record_date = st.date_input("Select Date", value=date.today())
    date_str = record_date.strftime("%Y-%m-%d")
    st.markdown(f"### Records for: {date_str}")

    # Load or Initialize Prices 
    if "prices" not in st.session_state:
        st.session_state.prices = load_prices()

    #Stock Sheet 
    st.header("Stock Sheet")
    stock_data = []
    for item in ITEMS:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            opening = st.number_input(f"{item} - Opening Stock", min_value=0, value=0, key=f"{item}_opening")
        with col2:
            purchases = st.number_input(f"{item} - Purchases", min_value=0, value=0, key=f"{item}_purchases")
        with col3:
            closing = st.number_input(f"{item} - Closing Stock", min_value=0, value=0, key=f"{item}_closing")
        with col4:
            price = st.number_input(f"{item} - Price per Item", min_value=0.0, value=st.session_state.prices.get(item, 0.0), key=f"{item}_price")
            st.session_state.prices[item] = price
        sales = opening + purchases - closing
        amount = sales * price
        with col5:
            st.write(f"Sales: {sales}")
            st.write(f"Amount: {amount:.2f}")
        stock_data.append([item, opening, purchases, closing, sales, price, amount])
    stock_df = pd.DataFrame(stock_data, columns=["Item", "Opening Stock", "Purchases", "Closing Stock", "Sales", "Price per Item", "Amount"])
    total_sales_amount = stock_df["Amount"].sum()
    st.markdown(f"Total Sales Amount: KES {total_sales_amount:,.2f}")
    save_prices(st.session_state.prices)

    # Accommodation Data
    st.header("Accommodation Data")
    accom_entries = []
    for i in range(5):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            first_floor = st.number_input(f"Row {i+1} - 1st Floor Rooms", min_value=0, value=0, key=f"accom_{i}_first")
        with col2:
            ground_floor = st.number_input(f"Row {i+1} - Ground Floor Rooms", min_value=0, value=0, key=f"accom_{i}_ground")
        with col3:
            money_lendered =

