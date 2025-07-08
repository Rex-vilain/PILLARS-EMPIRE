

import streamlit as st
import pandas as pd
import os
from datetime import date, datetime
from io import BytesIO

#Constants
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ITEMS = [
    "TUSKER", "PILISNER", "TUSKER MALT", "TUSKER LITE", "GUINESS KUBWA",
    "GUINESS SMALL", "BALOZICAN", "WHITE CAP", "BALOZI", "SMIRNOFF ICE",
    "SAVANNAH", "SNAPP", "TUSKER CIDER", "KINGFISHER", "ALLSOPPS",
    "G.K CAN", "T.LITE CAN", "GUARANA", "REDBULL", "RICHOT ½",
    "RICHOT ¼", "VICEROY ½", "VICEROY ¼", "VODKA½", "VODKA¼",
    "KENYACANE ¾", "KENYACANE ½", "KENYACANE ¼", "GILBEYS ½", "GILBEYS ¼",
    "V&A 750ml", "CHROME", "TRIPLE ACE", "BLACK AND WHITE", "KIBAO½",
    "KIBAO¼", "HUNTERS ½", "HUNTERS ¼", "CAPTAIN MORGAN", "KONYAGI",
    "V&A", "COUNTY", "BEST 750ml", "WATER 1L", "WATER½",
    "LEMONADE", "CAPRICE", "FAXE", "C.MORGAN", "VAT 69",
    "SODA300ML", "SODA500ML", "BLACK AND WHITE", "BEST", "CHROME 750ml",
    "MANGO", "TRUST", "PUNCH", "VODKA 750ml", "KONYAGI 500ml",
    "GILBEYS 750ml"
]

st.title("Pillars Bar & Restaurant Stock Sheet")

#Initialize or load dataframe in session state
if "df" not in st.session_state:
    df = pd.DataFrame({
        "Item": ITEMS,
        "Opening Stock": 0,
        "Purchases": 0,
        "Closing Stock": 0,
        "Selling Price": 0.0,
        "Sales": 0,
        "Amount": 0.0,
    })
    st.session_state.df = df
else:
    df = st.session_state.df

  #Editable columns
editable_cols = ["Opening Stock", "Purchases", "Closing Stock", "Selling Price"]

  #Show editable dataframe with those columns
edited_df = st.data_editor(df[["Item"] + editable_cols], num_rows="fixed", use_container_width=True)
 #Calculate sales and amount
edited_df["Sales"] = edited_df["Opening Stock"] + edited_df["Purchases"] - edited_df["Closing Stock"]
edited_df["Amount"] = edited_df["Sales"] * edited_df["Selling Price"]

  #Combine for full dataframe
full_df = edited_df.copy()

  #Update session state
st.session_state.df = full_df


  #Function to export to Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="StockSheet")
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

  #Download button for Excel file
excel_data = to_excel(full_df)
st.download_button(
    label="Download Stock Sheet as Excel",
    data=excel_data,
    file_name=f"pillars_stock_sheet_{pd.Timestamp.now().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

#View Past Records
st.header("📁 View Past Records")

view_date = st.date_input("Select date to view saved data")
filename = f"pillars_stock_sheet_{view_date}.xlsx"

if os.path.exists(filename):
    with open(filename, "rb") as file:
        st.download_button("Download This Record", file, file_name=filename)
        st.success("Record loaded. You can open or download it.")
else:
    st.warning("No record found for that date.")


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

    import streamlit as st
import pandas as pd
import os
from io import BytesIO


DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

 #Example stock items - replace with your real list
ITEMS = ["Item A", "Item B", "Item C"]

def get_filepath(date_str, section):
    return os.path.join(DATA_DIR, f"{section}_{date_str}.csv")

def load_section_df(date_str, section, default_df):
    path = get_filepath(date_str, section)
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return default_df

def save_section_df(date_str, section, df):
    path = get_filepath(date_str, section)
    df.to_csv(path, index=False)

st.title("Daily Business Tracker")

#Pick date for viewing/editing data
selected_date = st.date_input("Select Date")
date_str = selected_date.strftime("%Y-%m-%d")

#STOCK SHEET

st.header("Pillars Bar & Restaurant Stock Sheet")

stock_data = []
for item in ITEMS:
    opening = st.number_input(f"{item} - Opening Stock", min_value=0, value=0, key=f"{item}_opening")
    purchases = st.number_input(f"{item} - Purchases", min_value=0, value=0, key=f"{item}_purchases")
    closing = st.number_input(f"{item} - Closing Stock", min_value=0, value=0, key=f"{item}_closing")
    price = st.number_input(f"{item} - Selling Price", min_value=0.0, value=0.0, key=f"{item}_price")

    sales = opening + purchases - closing
    amount = sales * price

    stock_data.append({
        "Item": item,
        "Opening Stock": opening,
        "Purchases": purchases,
        "Closing Stock": closing,
        "Selling Price": price,
        "Sales": sales,
        "Amount": amount
    })

stock_df = pd.DataFrame(stock_data)
st.dataframe(stock_df)

st.markdown(f"Total Sales Amount: KES {stock_df['Amount'].sum():,.2f}")


#ACCOMMODATION DATA

st.header("Accommodation Data")

default_accom_df = pd.DataFrame({
    "Room Number": ["" for _ in range(10)],
    "1st Floor Rooms": ["" for _ in range(10)],
    "Ground Floor Rooms": ["" for _ in range(10)],
    "Money Lendered": [0.0 for _ in range(10)],
    "Payment Method": ["" for _ in range(10)],
})
accom_df = load_section_df(date_str, "accommodation", default_accom_df)

#Editable accommodation table
edited_accom_df = st.data_editor(accom_df, num_rows="dynamic", use_container_width=True)

#Calculate totals for rooms used (count unique non-empty rooms)
total_first_floor = edited_accom_df["1st Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
total_ground_floor = edited_accom_df["Ground Floor Rooms"].apply(lambda x: 1 if str(x).strip() else 0).sum()
total_lendered = edited_accom_df["Money Lendered"].sum()

st.markdown(f"Total 1st Floor Rooms Used: {total_first_floor}")
st.markdown(f"Total Ground Floor Rooms Used: {total_ground_floor}")
st.markdown(f"Total Money Lendered: KES {total_lendered:,.2f}")

if st.button("Save Accommodation Data"):
    save_section_df(date_str, "accommodation", edited_accom_df)
    st.success("Accommodation data saved!")
#EXPENSES

st.header("Expenses")

default_expenses_df = pd.DataFrame({
    "Description": ["" for _ in range(10)],
    "Amount": [0.0 for _ in range(10)],
})

expenses_df = load_section_df(date_str, "expenses", default_expenses_df)

edited_expenses_df = st.data_editor(expenses_df, num_rows="dynamic", use_container_width=True)

total_expenses = edited_expenses_df["Amount"].sum()
st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")

#MONEY PAID TO BOSS AND INVESTED

st.header("Money Transactions")

def load_money_val(date_str, key):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return float(f.read())
    return 0.0

def save_money_val(date_str, key, val):
    path = os.path.join(DATA_DIR, f"{key}_{date_str}.txt")
    with open(path, "w") as f:
        f.write(str(val))

money_paid = load_money_val(date_str, "money_paid")
money_invested = load_money_val(date_str, "money_invested")

money_paid_input = st.number_input("Money Paid to Boss", min_value=0.0, value=money_paid, step=1.0)
money_invested_input = st.number_input("Money Invested (e.g., from Chama)", min_value=0.0, value=money_invested, step=1.0)

if st.button("Save Money Transactions"):
    save_money_val(date_str, "money_paid", money_paid_input)
    save_money_val(date_str, "money_invested", money_invested_input)
    st.success("Money transactions saved!")

#SUMMARY

st.header("Summary")

total_sales_amount = edited_stock_df["Amount"].sum()
profit = total_sales_amount - total_expenses - money_paid_input

st.markdown(f"Total Sales Amount: KES {total_sales_amount:,.2f}")
st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")
st.markdown(f"Money Paid to Boss: KES {money_paid_input:,.2f}")
st.markdown(f"Money Invested: KES {money_invested_input:,.2f}")
st.markdown(f"Profit: KES {profit:,.2f}")
