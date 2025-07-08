

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
st.header("Accommodation Data Entry")

  #Initialize or load accommodation dataframe in session state
if "accom_df" not in st.session_state:
    accom_data = {
        "1st Floor Rooms": [0]*15,
        "Ground Floor Rooms": [0]*15,
        "Money Lendered": [0]*15,
        "Payment Method": ["Cash"]*15,
    }
    st.session_state.accom_df = pd.DataFrame(accom_data)
else:
    accom_df = st.session_state.accom_df

  #Editable columns
editable_cols = ["1st Floor Rooms", "Ground Floor Rooms", "Money Lendered", "Payment Method"]

  #Show editable dataframe (fixed number of rows)
edited_accom_df = st.data_editor(
    st.session_state.accom_df[editable_cols],
    num_rows="fixed",
    use_container_width=True,
)

  #Update session state with edited data
st.session_state.accom_df = edited_accom_df

  #Calculate totals
total_first_floor = edited_accom_df["1st Floor Rooms"].sum()
total_ground_floor = edited_accom_df["Ground Floor Rooms"].sum()
total_lendered = edited_accom_df["Money Lendered"].sum()

  #Show totals below
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

total_amount = full_df["Amount"].sum()  # Replace full_df with your stock dataframe variable
total_sales_amount = total_amount

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
