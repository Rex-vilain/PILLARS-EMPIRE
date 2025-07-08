

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
        "ITEM": ITEMS,
        "Opening Stock": 0,
        "Purchase": 0,
        "Closing Stock": 0,
        "Selling Price": 0.0,
        "Sales": 0,
        "Amount": 0.0,
    })
    st.session_state.df = df
else:
    df = st.session_state.df

  #Editable columns
editable_cols = ["Opening Stock", "Purchase", "Closing Stock", "Selling Price"]

  #Show editable dataframe with those columns
edited_df = st.data_editor(df[["Item"] + editable_cols])

 #Calculate sales and amount
edited_df["Sales"] = edited_df["Opening Stock"] + edited_df["Purchase"] - edited_df["Closing Stock"]
edited_df["Amount"] = edited_df["Sales"] * edited_df["Selling Price"]

  #Combine for full dataframe
full_df = pd.concat([edited_df, edited_df[["Sales", "Amount"]]], axis=1)

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

#Accommodation Data 
st.header("Accommodation Data")

accom_data = []
num_rows = 15  # You can adjust this as needed

for i in range(num_rows):
    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
    with col1:
        first_floor = st.number_input(f"Row {i+1} - 1st Floor Rooms", min_value=0, value=0, key=f"first_{i}")
    with col2:
        ground_floor = st.number_input(f"Row {i+1} - Ground Floor Rooms", min_value=0, value=0, key=f"ground_{i}")
    with col3:
        lendered = st.number_input(f"Row {i+1} - Money Lendered", min_value=0, value=0, key=f"lendered_{i}")
    with col4:
        payment_method = st.selectbox(f"Row {i+1} - Payment Method", ["Cash", "M-Pesa", "Other"], key=f"method_{i}")
    
    accom_data.append({
        "1st Floor Rooms": first_floor,
        "Ground Floor Rooms": ground_floor,
        "Money Lendered": lendered,
        "Payment Method": payment_method
    })

accom_df = pd.DataFrame(accom_data)
total_first_floor = accom_df["1st Floor Rooms"].sum()
total_ground_floor = accom_df["Ground Floor Rooms"].sum()
total_lendered = accom_df["Money Lendered"].sum()

st.dataframe(accom_df)
st.markdown(f"Total 1st Floor Rooms: {total_first_floor}")
st.markdown(f"Total Ground Floor Rooms: {total_ground_floor}")
st.markdown(f"Total Money Lendered: KES {total_lendered:,.2f}")

#Expenses Entry 
st.header("Daily Expenses")

if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = pd.DataFrame(columns=["Item", "Amount"])

expenses_df = st.data_editor(
    st.session_state.expenses_df,
    num_rows="dynamic",
    key="expenses_editor"
)

total_expenses = expenses_df["Amount"].sum() if "Amount" in expenses_df else 0
st.markdown(f"Total Expenses: KES {total_expenses:,.2f}")

#Money Paid to Boss 
st.subheader("Money Paid to Boss")
money_paid = st.number_input("Enter amount paid to boss", min_value=0, value=0)

#Money Invested from Chama 
st.subheader("Money Invested (e.g., from Chama)")
money_invested = st.number_input("Enter amount invested", min_value=0, value=0)

#Summary & Profit Calculation
st.header("Summary")

total_sales_amount = total_amount  # Assuming this was calculated from stock & accommodation

net_profit = (total_sales_amount + money_invested) - (total_expenses + money_paid)
st.markdown(f"Total Sales Amount: KES {total_sales_amount:,.2f}")
st.markdown(f"Net Profit: KES {net_profit:,.2f}")

#Save & Download Data 
st.header("Save & Download Daily Report")

if st.button("Save Data"):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = "daily_reports"
    os.makedirs(folder, exist_ok=True)

    # Save all data
    stock_df.to_csv(f"{folder}/stock_{date_str}.csv", index=False)
    accom_df.to_csv(f"{folder}/accommodation_{date_str}.csv", index=False)
    expenses_df.to_csv(f"{folder}/expenses_{date_str}.csv", index=False)

    # Summary file
    summary = {
        "Total Sales": [total_sales_amount],
        "Expenses": [total_expenses],
        "Money Paid to Boss": [money_paid],
        "Money Invested": [money_invested],
        "Profit": [net_profit]
    }
    pd.DataFrame(summary).to_csv(f"{folder}/summary_{date_str}.csv", index=False)

    st.success("Data saved successfully!")

#Download Reports 
st.header("View & Download Past Reports")
report_files = os.listdir("daily_reports") if os.path.exists("daily_reports") else []

for file in report_files:
    with open(f"daily_reports/{file}", "rb") as f:
        st.download_button(label=f"Download {file}", data=f, file_name=file)
