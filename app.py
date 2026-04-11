import streamlit as st
import pandas as pd
from db import *

st.set_page_config(page_title="Slot Booking System")

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = login_user(username, password)

        if role:
            st.session_state.logged_in = True
            st.session_state.role = role
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ================= MAIN =================
role = st.session_state.role

st.title("📅 Slot Booking System")
st.write(f"👤 Logged in as: {role}")

if st.button("Logout"):
    st.session_state.clear()
    st.rerun()

# ================= SLOT LOCK =================
if role in ["execution", "admin"]:
    st.subheader("🔒 Lock Slots")

    config_date = st.date_input("Select Date for Lock")
    max_slots = st.number_input("Max Slots", 1, 41, 8)

    if st.button("Lock Slots"):
        set_max_slots(str(config_date), max_slots)
        st.success("Slots locked successfully")

# ================= BOOKING =================
if role in ["sales", "execution", "admin"]:
    st.subheader("📝 Book Slots")

    jr_id = st.text_input("JR Number")
    salesperson = st.text_input("Salesperson Name")
    client_name = st.text_input("Client Name")
    from datetime import date as dt_date

    date = st.date_input(
        "Select Date",
        min_value=dt_date.today())

    if date:
        date_str = str(date)

        slots = get_available_slots(date_str)
        st.write(f"Available Slots: {slots}")

        selected_slots = st.multiselect("Select Slots", slots)

        if st.button("Book Slots"):
            if not jr_id:
                st.warning("Enter JR Number")

            elif not salesperson:
                st.warning("Enter Salesperson Name")

            elif not selected_slots:
                st.warning("Select slots")

            else:
                success, msg = book_with_limit(
                    jr_id,
                    client_name,
                    salesperson,
                    date_str,
                    selected_slots
                )

                if success:
                    st.success(msg)
                else:
                    st.error(msg)


# ================= EDIT BOOKINGS =================

if role in ["execution", "admin"]:
    st.subheader("✏️ Manage Bookings")

    filter_date = st.date_input("Select Date to View Bookings")

    bookings = get_all_bookings()

    if not bookings:
        st.info("No bookings available")

    else:
        # ✅ Filter by selected date
        filtered = [
            b for b in bookings
            if str(b["slot_date"]) == str(filter_date)
        ]

        if not filtered:
            st.info("No bookings for selected date")

        else:
            for b in filtered:
                st.write(
                    f"ID: {b['booking_id']} | {b['client_name']} | {b['slot_date']} | Slot {b['slot_number']}"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    new_date = st.date_input(
                        "New Date",
                        key=f"d{b['booking_id']}"
                    )

                with col2:
                    new_slot = st.number_input(
                        "Slot", 1, 16,
                        key=f"s{b['booking_id']}"
                    )

                with col3:
                    if st.button("Update", key=f"u{b['booking_id']}"):
                        update_booking(
                            b["booking_id"],
                            str(new_date),
                            new_slot
                        )
                        st.success("Updated")

                    if st.button("Delete", key=f"del{b['booking_id']}"):
                        delete_booking(b["booking_id"])
                        st.warning("Deleted")

# ================= DASHBOARD =================
st.subheader("📊 Dashboard")

filter_date = st.date_input("Date")

if st.button("Load Data"):
    data = get_all_bookings()

    if not data:
        st.info("No bookings available")
    else:
        df = pd.DataFrame(data)

        if filter_date:
            df = df[df["slot_date"] == str(filter_date)]

        if df.empty:
            st.info("No bookings for selected date")
        else:
            st.dataframe(df)