from datetime import datetime, timedelta
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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

def append_to_gsheet(data_dict, sheet_name='Sheet1'):
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("psychic-rush-459809-t8-a81dbb6aa47b.json", scopes=scope)
    client = gspread.authorize(creds)
    
    # Open the Google Sheet (replace with your sheet name or URL)
    sheet = client.open("Test").worksheet(sheet_name)
    
    # Prepare the row in the correct order
    headers = sheet.row_values(1)
    row = [data_dict.get(h, "") for h in headers]
    sheet.append_row(row)
    print("Data appended to Google Sheet")

    

def main():

    st.markdown("### 🍱 Place Your Tiffin Order")
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

    with st.form('tiffin_form'):
        # Per-date tiffin options
        per_date_tiffin = {}
        full_price = 120
        half_price = 70
        if selected_days:
            st.markdown("### Tiffin Preferences for Each Date")
            for date_info in selected_days:
                with st.container():
                    st.markdown(f"**{date_info['date']} ({date_info['day']})**")
                    half_tiffin_count_col, full_tiffin_count_col = st.columns(2)
                    with half_tiffin_count_col:
                        half_tiffin_count = st.number_input(
                            f"Number of Half Tiffins for {date_info['date']}",
                            min_value=0, max_value=20, step=1,
                            key=f"half_tiffins_{date_info['full_date']}"
                        )
                    with full_tiffin_count_col:
                        full_tiffin_count = st.number_input(
                            f"Number of Full Tiffins for {date_info['date']}",
                            min_value=0, max_value=20, step=1,
                            key=f"full_tiffins_{date_info['full_date']}"
                        )
                    per_date_tiffin[date_info['full_date']] = {
                        'half_tiffin_count': half_tiffin_count,
                        'full_tiffin_count': full_tiffin_count
                    }

        # Dessert section
        st.markdown("### 🍰 Optional Desserts")
        st.markdown("Select any desserts you'd like to add to your order")
        
        dessert_prices = {
            'Gulab Jamun': 20,
            'Rasgulla': 20,
            'Ice Cream': 30,
            'Kheer': 25
        }
        
        selected_desserts = {}
        dessert_cols = st.columns(2)
        for i, (dessert, price) in enumerate(dessert_prices.items()):
            with dessert_cols[i % 2]:
                quantity = st.number_input(
                    f"{dessert} (₹{price})",
                    min_value=0,
                    max_value=10,
                    value=0,
                    key=f"dessert_{dessert}"
                )
                if quantity > 0:
                    selected_desserts[dessert] = {
                        'quantity': quantity,
                        'price': price
                    }
        
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input('Full Name *', max_chars=100)
            contact = st.text_input('Contact Number *', max_chars=20)
            address = st.text_area('Delivery Address *', max_chars=300, 
                                 help="Please provide complete address for delivery")
        
        with col2:
            instructions = st.text_area('Special Instructions', max_chars=500,
                                      help="Any special dietary requirements or delivery instructions")

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
            if not pd.get('half_tiffin_count'):
                missing_fields.append(f"Tiffin Type for {date_info['date']}")
            if not pd.get('full_tiffin_count'):
                missing_fields.append(f"Number of Tiffins for {date_info['date']}")
        if missing_fields:
            st.error(f'Please fill all required fields marked with *: {", ".join(missing_fields)}')
        else:
            # Calculate total price
            total_tiffin_price = 0
            tiffin_details = []
            for date_info in selected_days:
                pd = per_date_tiffin[date_info['full_date']]
                half_tiffin_count = pd['half_tiffin_count']
                full_tiffin_count = pd['full_tiffin_count']
                #tiffin_type = pd['tiffin_type']
                #tiffins = pd['tiffins']
                total_tiffin_price += half_tiffin_count * half_price + full_tiffin_count * full_price
                tiffin_details.append(f"{date_info['date']} ({date_info['day']}): {half_tiffin_count} half tiffins and {full_tiffin_count} full tiffins")
            total_dessert_price = sum(d['quantity'] * d['price'] for d in selected_desserts.values())
            total_price = total_tiffin_price + total_dessert_price
            
            # Prepare data
            data = {
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Name': name,
                'Contact Number': contact,
                'Address': address,
                'Tiffin Details': '; '.join(tiffin_details),
                'Desserts': ', '.join([f"{dessert} x {details['quantity']}" for dessert, details in selected_desserts.items()]) if selected_desserts else 'None',
                'Special Instructions': instructions,
                'Total Price': total_price
            }

            append_to_gsheet(data)

if __name__ == '__main__':
    main() 