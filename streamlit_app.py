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
            with st.expander(f"📅 {date_info['date']} ({date_info['day']})", expanded=False):
                day_menu = menu.get(date_info['day'], None)
                
                if day_menu:
                    # Create tabs for Lunch and Dinner
                    lunch_tab, dinner_tab = st.tabs(["🍽️ Lunch", "🌙 Dinner"])
                    
                    # Lunch Tab
                    with lunch_tab:
                        st.markdown("**Lunch Options:**")
                        # 2x2 grid for tiffin menus and inputs
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
                                lunch_full_tiffin_count = st.number_input(
                                    f"Number of Full Tiffins for Lunch",
                                    min_value=0, max_value=20, step=1,
                                    key=f"lunch_full_tiffins_{date_info['full_date']}"
                                )
                            else:
                                lunch_full_tiffin_count = 0
                        with grid_cols2[1]:
                            if 'half_tiffin' in day_menu:
                                lunch_half_tiffin_count = st.number_input(
                                    f"Number of Half Tiffins for Lunch",
                                    min_value=0, max_value=20, step=1,
                                    key=f"lunch_half_tiffins_{date_info['full_date']}"
                                )
                            else:
                                lunch_half_tiffin_count = 0
                        
                        # Extra items for lunch
                        extra_items = menu.get('extra_items', {})
                        if extra_items:
                            st.markdown("**Extra Items for Lunch:**")
                            extra_item_counts_lunch = {}
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
                                                key=f"lunch_extra_{item}_{date_info['full_date']}"
                                            )
                                            extra_item_counts_lunch[item] = qty
                        else:
                            extra_item_counts_lunch = {}
                    
                    # Dinner Tab
                    with dinner_tab:
                        st.markdown("**Dinner Options:**")
                        # 2x2 grid for tiffin menus and inputs
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
                                dinner_full_tiffin_count = st.number_input(
                                    f"Number of Full Tiffins for Dinner",
                                    min_value=0, max_value=20, step=1,
                                    key=f"dinner_full_tiffins_{date_info['full_date']}"
                                )
                            else:
                                dinner_full_tiffin_count = 0
                        with grid_cols2[1]:
                            if 'half_tiffin' in day_menu:
                                dinner_half_tiffin_count = st.number_input(
                                    f"Number of Half Tiffins for Dinner",
                                    min_value=0, max_value=20, step=1,
                                    key=f"dinner_half_tiffins_{date_info['full_date']}"
                                )
                            else:
                                dinner_half_tiffin_count = 0
                        
                        # Extra items for dinner
                        if extra_items:
                            st.markdown("**Extra Items for Dinner:**")
                            extra_item_counts_dinner = {}
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
                                                key=f"dinner_extra_{item}_{date_info['full_date']}"
                                            )
                                            extra_item_counts_dinner[item] = qty
                        else:
                            extra_item_counts_dinner = {}
                    
                    # Store data for both lunch and dinner
                    per_date_tiffin[date_info['full_date']] = {
                        'lunch': {
                            'half_tiffin_count': lunch_half_tiffin_count if 'half_tiffin' in day_menu else 0,
                            'full_tiffin_count': lunch_full_tiffin_count if 'full_tiffin' in day_menu else 0,
                            'extra_items': extra_item_counts_lunch
                        },
                        'dinner': {
                            'half_tiffin_count': dinner_half_tiffin_count if 'half_tiffin' in day_menu else 0,
                            'full_tiffin_count': dinner_full_tiffin_count if 'full_tiffin' in day_menu else 0,
                            'extra_items': extra_item_counts_dinner
                        }
                    }
                else:
                    st.markdown(":grey_question: Menu not available for this day.")
        
        

    with st.form('tiffin_form'):
        # Per-date tiffin options
        full_price = 120
        half_price = 70
        

        # Calculate live total price and create detailed summary
        total_tiffin_price = 0
        tiffin_details = []
        order_summary = []
        
        if selected_days:
            for date_info in selected_days:
                pd = per_date_tiffin.get(date_info['full_date'], {})
                
                # Lunch calculations
                lunch_data = pd.get('lunch', {})
                lunch_half_tiffin_count = lunch_data.get('half_tiffin_count', 0)
                lunch_full_tiffin_count = lunch_data.get('full_tiffin_count', 0)
                lunch_extra_items = lunch_data.get('extra_items', {})
                
                # Dinner calculations
                dinner_data = pd.get('dinner', {})
                dinner_half_tiffin_count = dinner_data.get('half_tiffin_count', 0)
                dinner_full_tiffin_count = dinner_data.get('full_tiffin_count', 0)
                dinner_extra_items = dinner_data.get('extra_items', {})
                
                # Calculate tiffin price for lunch
                lunch_half_price = lunch_half_tiffin_count * (menu.get(date_info['day'], {}).get('half_tiffin', {}).get('cost', 0))
                lunch_full_price = lunch_full_tiffin_count * (menu.get(date_info['day'], {}).get('full_tiffin', {}).get('cost', 0))
                total_tiffin_price += lunch_half_price + lunch_full_price
                
                # Calculate tiffin price for dinner
                dinner_half_price = dinner_half_tiffin_count * (menu.get(date_info['day'], {}).get('half_tiffin', {}).get('cost', 0))
                dinner_full_price = dinner_full_tiffin_count * (menu.get(date_info['day'], {}).get('full_tiffin', {}).get('cost', 0))
                total_tiffin_price += dinner_half_price + dinner_full_price
                
                # Calculate extra items price for lunch
                lunch_extras_price = 0
                for item, qty in lunch_extra_items.items():
                    item_cost = menu.get('extra_items', {}).get(item, {}).get('cost', 0)
                    lunch_extras_price += qty * item_cost
                    total_tiffin_price += qty * item_cost
                
                # Calculate extra items price for dinner
                dinner_extras_price = 0
                for item, qty in dinner_extra_items.items():
                    item_cost = menu.get('extra_items', {}).get(item, {}).get('cost', 0)
                    dinner_extras_price += qty * item_cost
                    total_tiffin_price += qty * item_cost
                
                # Create detailed summary for order submission
                lunch_summary = f"Lunch: {lunch_half_tiffin_count} half, {lunch_full_tiffin_count} full"
                dinner_summary = f"Dinner: {dinner_half_tiffin_count} half, {dinner_full_tiffin_count} full"
                
                lunch_extras = ', '.join([f'{item} x{qty}' for item, qty in lunch_extra_items.items() if qty > 0])
                dinner_extras = ', '.join([f'{item} x{qty}' for item, qty in dinner_extra_items.items() if qty > 0])
                
                if lunch_extras:
                    lunch_summary += f", Extras: {lunch_extras}"
                if dinner_extras:
                    dinner_summary += f", Extras: {dinner_extras}"
                
                tiffin_details.append(
                    f"{date_info['date']} ({date_info['day']}): {lunch_summary}; {dinner_summary}"
                )
                
                # Create detailed order summary for display
                day_total = lunch_half_price + lunch_full_price + dinner_half_price + dinner_full_price + lunch_extras_price + dinner_extras_price
                if day_total > 0:
                    order_summary.append({
                        'date': f"{date_info['date']} ({date_info['day']})",
                        'lunch': {
                            'half': lunch_half_tiffin_count,
                            'full': lunch_full_tiffin_count,
                            'extras': lunch_extra_items,
                            'price': lunch_half_price + lunch_full_price + lunch_extras_price
                        },
                        'dinner': {
                            'half': dinner_half_tiffin_count,
                            'full': dinner_full_tiffin_count,
                            'extras': dinner_extra_items,
                            'price': dinner_half_price + dinner_full_price + dinner_extras_price
                        },
                        'day_total': day_total
                    })

        # Display Order Summary
        if order_summary:
            st.markdown("### 📋 Order Summary")
            st.markdown("Here's a breakdown of your selections:")
            
            for day_order in order_summary:
                with st.expander(f"📅 {day_order['date']} - ₹{day_order['day_total']}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🍽️ Lunch**")
                        lunch = day_order['lunch']
                        if lunch['half'] > 0 or lunch['full'] > 0:
                            if lunch['half'] > 0:
                                st.markdown(f"• Half Tiffin: {lunch['half']} × ₹{menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('half_tiffin', {}).get('cost', 0)} = ₹{lunch['half'] * menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('half_tiffin', {}).get('cost', 0)}")
                            if lunch['full'] > 0:
                                st.markdown(f"• Full Tiffin: {lunch['full']} × ₹{menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('full_tiffin', {}).get('cost', 0)} = ₹{lunch['full'] * menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('full_tiffin', {}).get('cost', 0)}")
                        else:
                            st.markdown("• No lunch ordered")
                        
                        # Show lunch extras
                        lunch_extras_list = [f"{item} × {qty} × ₹{menu.get('extra_items', {}).get(item, {}).get('cost', 0)} = ₹{qty * menu.get('extra_items', {}).get(item, {}).get('cost', 0)}" 
                                           for item, qty in lunch['extras'].items() if qty > 0]
                        if lunch_extras_list:
                            st.markdown("**Extra Items:**")
                            for extra in lunch_extras_list:
                                st.markdown(f"• {extra}")
                        
                        if lunch['price'] > 0:
                            st.markdown(f"**Lunch Total: ₹{lunch['price']}**")
                    
                    with col2:
                        st.markdown("**🌙 Dinner**")
                        dinner = day_order['dinner']
                        if dinner['half'] > 0 or dinner['full'] > 0:
                            if dinner['half'] > 0:
                                st.markdown(f"• Half Tiffin: {dinner['half']} × ₹{menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('half_tiffin', {}).get('cost', 0)} = ₹{dinner['half'] * menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('half_tiffin', {}).get('cost', 0)}")
                            if dinner['full'] > 0:
                                st.markdown(f"• Full Tiffin: {dinner['full']} × ₹{menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('full_tiffin', {}).get('cost', 0)} = ₹{dinner['full'] * menu.get(day_order['date'].split(' (')[1].rstrip(')'), {}).get('full_tiffin', {}).get('cost', 0)}")
                        else:
                            st.markdown("• No dinner ordered")
                        
                        # Show dinner extras
                        dinner_extras_list = [f"{item} × {qty} × ₹{menu.get('extra_items', {}).get(item, {}).get('cost', 0)} = ₹{qty * menu.get('extra_items', {}).get(item, {}).get('cost', 0)}" 
                                            for item, qty in dinner['extras'].items() if qty > 0]
                        if dinner_extras_list:
                            st.markdown("**Extra Items:**")
                            for extra in dinner_extras_list:
                                st.markdown(f"• {extra}")
                        
                        if dinner['price'] > 0:
                            st.markdown(f"**Dinner Total: ₹{dinner['price']}**")
                    
                    st.markdown(f"**Day Total: ₹{day_order['day_total']}**")
        else:
            st.info("📋 **No orders selected yet.** Please select dates and choose your tiffin preferences above.")

        st.info(f"**Total Price: ₹{total_tiffin_price}**")

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
        
        # Check minimum order value
        if total_tiffin_price < 100:
            st.error(f'❌ **Minimum order value is ₹100.** Your current total is ₹{total_tiffin_price}. Please add more items to your order.')
        elif missing_fields:
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