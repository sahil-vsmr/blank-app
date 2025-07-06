from datetime import datetime, timedelta
import streamlit as st
from PIL import Image
import yaml
import gspread
from google.oauth2.service_account import Credentials
import os
import json


# st.title("🎈 My new app v2")
# st.write(
#     "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
# )



def get_week_dates():
    """Get dates for the current week"""
    today = datetime.now()
    if today.weekday() > 2:  # Wednesday is 2
        days_until_monday = (7 - today.weekday()) % 7
        start_date = today + timedelta(days=days_until_monday)
    else:
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
    
    dates = []
    for i in range(6):  # Monday to Saturday
        current_date = start_date + timedelta(days=i)
        dates.append({
            'date': current_date.strftime('%d %b'),
            'day': current_date.strftime('%A'),
            'full_date': current_date.strftime('%Y-%m-%d')
        })
    return dates

def append_to_gsheet_test(data_dict, sheet_name='Sheet1'):
    # Use streamlit_gsheets connection
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Use environment variable for cloud deployment
    if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
        # Parse JSON from environment variable
        service_account_info = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    else:
        # Fallback to file for local development
        creds = Credentials.from_service_account_file("psychic-rush-459809-t8-a81dbb6aa47b.json", scopes=scope)
    
    client = gspread.authorize(creds)
    
    # Open the Google Sheet (replace with your sheet name or URL)
    sheet = client.open("Test").worksheet(sheet_name)
    
    # Prepare the row in the correct order
    headers = sheet.row_values(1)
    row = [data_dict.get(h, "") for h in headers]
    sheet.append_row(row)
    print("Data appended to Google Sheet")

def append_to_gsheet_gspread(data_dict, spreadsheet_name="TiffinOrderSheet", sheet_name='Sheet1'):
    """
    Append data to Google Sheets using gspread with better error handling
    
    Args:
        data_dict (dict): Dictionary containing the data to append
        spreadsheet_name (str): Name of the Google Spreadsheet
        sheet_name (str): Name of the worksheet within the spreadsheet
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Define the scope for Google Sheets API
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Initialize credentials
        if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
            # For cloud deployment - use environment variable
            service_account_info = json.loads(os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'])
            creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        else:
            # For local development - use service account file
            creds = Credentials.from_service_account_file("ambient-polymer-465105-h1-aeb54163f0c7.json", scopes=scope)
        
        # Authorize the client
        client = gspread.authorize(creds)
        
        # Open the spreadsheet
        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            print(f"Error: Spreadsheet '{spreadsheet_name}' not found")
            return False
        
        # Open the worksheet
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            print(f"Error: Worksheet '{sheet_name}' not found in spreadsheet '{spreadsheet_name}'")
            return False
        
        # Get headers from the first row
        headers = worksheet.row_values(1)
        
        if not headers:
            print("Error: No headers found in the first row")
            return False
        
        # Prepare the row data in the correct order based on headers
        row_data = []
        for header in headers:
            value = data_dict.get(header, "")
            # Convert None to empty string
            if value is None:
                value = ""
            row_data.append(str(value))
        
        # Append the row to the worksheet
        worksheet.append_row(row_data)
        
        print(f"Successfully appended data to '{spreadsheet_name}' - '{sheet_name}'")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error parsing Google credentials JSON: {e}")
        return False
    except Exception as e:
        print(f"Error appending to Google Sheets: {e}")
        return False

# def append_to_gsheet(data_dict, sheet_name='Sheet1'):
#     conn = st.connection("gsheets", type=GSheetsConnection)
#     data = conn.read()
#     print(data)
#     st.dataframe(data)
    
#     # Check if sheet is empty
#     if data.empty:
#         print("Sheet is empty, adding data_dict...")
#         # Create DataFrame from data_dict and update the sheet
#         df = pd.DataFrame([data_dict])
#         conn.update(data=df, worksheet=sheet_name)
#         print("Data added to empty sheet")
#     else:
#         print("Sheet is not empty, appending new data...")
#         # Create DataFrame from new data_dict
#         new_df = pd.DataFrame([data_dict])
#         # Combine existing data with new data
#         combined_df = pd.concat([data, new_df], ignore_index=True)
#         # Update the sheet with combined data
#         conn.update(data=combined_df, worksheet=sheet_name)
#         print("New data appended to existing data")
#         print("Combined data:")
#         print(combined_df)

def load_menu(filename="day-menu.yaml"):
    with open(filename, 'r') as f:
        menu_raw = yaml.safe_load(f)
    # Handle duplicate days: keep only the first occurrence for each day
    menu = {}
    for day, items in menu_raw.items():
        if day not in menu:
            menu[day] = items
    return menu

def main():

    st.markdown("### 🍱 Place Your Tiffin Order")
    st.markdown("Healthy Food Bank's (HFB) Vishmukt Tiffin Service - Head Chef- Dr. Pratibha Kolte Tai | Communication - Shubham Shelke (8484846121)")
    st.markdown("Fill out the form below to place your tiffin order for the week.")

    st.markdown("### Select Dates for Tiffin Service *")
    st.markdown("Choose the dates you want tiffin service. You can select multiple dates.")
    week_dates = get_week_dates()
    date_options = [f"{d['date']} ({d['day']})" for d in week_dates]
    date_map = {f"{d['date']} ({d['day']})": d for d in week_dates}
    selected_date_labels = st.multiselect(
        'Select Dates',
        options=date_options,
    )
    selected_days = [date_map[label] for label in selected_date_labels]

    menu = load_menu()

    per_date_tiffin = {}

    if selected_days:
            st.markdown("### Tiffin Preferences for Each Date")
            for date_info in selected_days:
                with st.container():
                    st.markdown(f"**{date_info['date']} ({date_info['day']})**")
                    day_menu = menu.get(date_info['day'], None)
                    # 2x2 grid for tiffin menus and inputs
                    if day_menu:
                        grid_cols = st.columns(2)
                        # First row: menus
                        with grid_cols[0]:
                            if 'full_tiffin' in day_menu:
                                st.markdown(f"<b>Full Tiffin (₹{day_menu['full_tiffin']['cost']}):</b>", unsafe_allow_html=True)
                                st.markdown("\n".join([f"- {item}" for item in day_menu['full_tiffin']['items']]))
                        with grid_cols[1]:
                            if 'half_tiffin' in day_menu:
                                st.markdown(f"<b>Half Tiffin (₹{day_menu['half_tiffin']['cost']}):</b>", unsafe_allow_html=True)
                                st.markdown("\n".join([f"- {item}" for item in day_menu['half_tiffin']['items']]))
                        # Second row: number inputs
                        grid_cols2 = st.columns(2)
                        with grid_cols2[0]:
                            if 'full_tiffin' in day_menu:
                                full_tiffin_count = st.number_input(
                                    f"Number of Full Tiffins for {date_info['date']}",
                                    min_value=0, max_value=20, step=1,
                                    key=f"full_tiffins_{date_info['full_date']}"
                                )
                            else:
                                full_tiffin_count = 0
                        with grid_cols2[1]:
                            if 'half_tiffin' in day_menu:
                                half_tiffin_count = st.number_input(
                                    f"Number of Half Tiffins for {date_info['date']}",
                                    min_value=0, max_value=20, step=1,
                                    key=f"half_tiffins_{date_info['full_date']}"
                                )
                            else:
                                half_tiffin_count = 0
                    else:
                        st.markdown(":grey_question: Menu not available for this day.")
                    bread_choices = ['Chapati', 'Bhakri']
                    ukdiche_modak_prices = ['4 - Rs. 200', '6 - Rs. 300', '8 - Rs. 400']
                
                    # with zero_masala_tiffin_check:
                    #     zero_masala_tiffin = st.toggle(
                    #         f"Want Zero Masala Tiffin?",
                    #         value=False,
                    #         key=f"zero_masala_tiffin_{date_info['full_date']}"
                    #     )
                    # with bread_choice: 
                    #     bread_choice = st.selectbox(
                    #         f"Choose an option for bread",
                    #         options=bread_choices,
                    #         key=f"bread_choice_{date_info['full_date']}",
                    #         help="Chapati includes: 2 rotis, 1 sabzi, dal, and rice."
                    #     )
                    # with dessert_choice:
                    #     if 'Friday' in date_info['day']:
                    #         dessert_choice = st.selectbox(
                    #             f"Ukdiche Modak (Pcs.)",
                    #             options=ukdiche_modak_prices,
                    #             key=f"dessert_choice_{date_info['full_date']}",
                    #             help="Choose an option for dessert",
                    #         )
                    #     else:
                    #         dessert_choice = "NA"
                    # Extra items section'''
                    extra_items = menu.get('extra_items', {})
                    if extra_items:
                        st.markdown('<b>Extra Items:</b>', unsafe_allow_html=True)
                        extra_item_counts = {}
                        extra_item_list = []
                        for item, details in extra_items.items():
                            # Only show item if 'days' is not present or if this day is in 'days'
                            if not details.get('days') or date_info['day'] in details['days']:
                                extra_item_list.append((item, details))
                        n_cols = 3
                        n_rows = 2
                        for row in range(n_rows):
                            cols = st.columns(n_cols)
                            for col_idx in range(n_cols):
                                item_idx = row * n_cols + col_idx
                                if item_idx < len(extra_item_list):
                                    item, details = extra_item_list[item_idx]
                                    with cols[col_idx]:
                                        qty = st.number_input(
                                            f"{item} (₹{details['cost']} each)",
                                            min_value=0, max_value=20, step=1,
                                            key=f"extra_{item}_{date_info['full_date']}"
                                        )
                                        extra_item_counts[item] = qty
                    else:
                        extra_item_counts = {}
                    per_date_tiffin[date_info['full_date']] = {
                        'half_tiffin_count': half_tiffin_count if 'half_tiffin' in day_menu else 0,
                        'full_tiffin_count': full_tiffin_count if 'full_tiffin' in day_menu else 0,
                        'extra_items': extra_item_counts
                    }
        
        

    with st.form('tiffin_form'):
        # Per-date tiffin options
        full_price = 120
        half_price = 70
        

        # Calculate live total price
        total_tiffin_price = 0
        tiffin_details = []
        if selected_days:
            for date_info in selected_days:
                pd = per_date_tiffin.get(date_info['full_date'], {})
                half_tiffin_count = pd.get('half_tiffin_count', 0)
                full_tiffin_count = pd.get('full_tiffin_count', 0)
                # Calculate tiffin price
                total_tiffin_price += half_tiffin_count * (menu.get(date_info['day'], {}).get('half_tiffin', {}).get('cost', 0))
                total_tiffin_price += full_tiffin_count * (menu.get(date_info['day'], {}).get('full_tiffin', {}).get('cost', 0))
                # Calculate extra items price
                extra_items = pd.get('extra_items', {})
                for item, qty in extra_items.items():
                    item_cost = menu.get('extra_items', {}).get(item, {}).get('cost', 0)
                    total_tiffin_price += qty * item_cost
                tiffin_details.append(
                    f"""
                    {date_info['date']} ({date_info['day']}):
                    {half_tiffin_count} half tiffins,
                    {full_tiffin_count} full tiffins,
                    Extra items: {', '.join([f'{item} x{qty}' for item, qty in extra_items.items() if qty > 0])}
                    """
                )

        #total_dessert_price = sum(d['quantity'] * d['price'] for d in selected_desserts.values())
        #total_price = total_tiffin_price + total_dessert_price

        st.info(f"**Total Price (so far): ₹{total_tiffin_price}**")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input('Full Name *', max_chars=100)
            contact = st.text_input('Contact Number *', max_chars=20)
            address = st.text_area('Delivery Address *', max_chars=300, 
                                 help="Please provide complete address for delivery")
        
        with col2:
            instructions = st.text_area('Special Instructions', max_chars=500,
                                      help="Any special dietary requirements or delivery instructions")


        uploaded_file = st.file_uploader("Upload a screenshot", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Screenshot", use_container_width=True)

        st.markdown("---")
        st.markdown("* Required fields")

        submitted = st.form_submit_button('Submit Order')

    if submitted:
        missing_fields = []
        if not name:
            missing_fields.append("Name")
        if not contact:
            missing_fields.append("Contact Number")
        if not address:
            missing_fields.append("Address")
        if not selected_days:
            missing_fields.append("Dates")
        for date_info in selected_days:
            pd = per_date_tiffin.get(date_info['full_date'], {})
        if missing_fields:
            st.error(f'Please fill all required fields marked with *: {", ".join(missing_fields)}')
        else:
            # Prepare data
            data = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Name': name,
                'Contact Number': contact,
                'Address': address,
                'Tiffin Details': '; '.join(tiffin_details),
                'Special Instructions': instructions,
                'Total Price': total_tiffin_price
            }

            # Show loading spinner while submitting
            with st.spinner("🔄 Submitting your order to the kitchen..."):
                if append_to_gsheet_gspread(data):
                    st.success("✅ Order submitted successfully! Your tiffin order has been sent to the kitchen.")
                else:
                    st.error("❌ Failed to submit order. Please try again or contact support if the problem persists.")

if __name__ == '__main__':
    main() 