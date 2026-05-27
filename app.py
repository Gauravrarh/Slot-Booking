import streamlit as st
import pandas as pd

from booking_engine import *

st.set_page_config(
    page_title="Slot Booking System",
    page_icon="📅",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.metric-card {
    background: linear-gradient(145deg, #1f2937, #111827);
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid #2d3748;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.25);
}

.metric-title {
    font-size: 18px;
    color: #9ca3af;
}

.metric-value {
    font-size: 38px;
    font-weight: bold;
    color: white;
}

.slot-card {
    background: linear-gradient(145deg, #1e293b, #111827);
    border: 1px solid #334155;
    padding: 16px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 12px;
    transition: 0.3s;
}

.slot-title {
    color: white;
    font-size: 20px;
    font-weight: bold;
}

.section-box {
    background-color: #111827;
    padding: 20px;
    border-radius: 18px;
    border: 1px solid #1f2937;
    margin-bottom: 20px;
}

.small-text {
    color: #9ca3af;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# ================= LOGIN PAGE =================
if not st.session_state.logged_in:

    st.markdown(
        "<h1 style='text-align:center;'>📅 Slot Booking System</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;color:gray;'>"
        "Multi-User JR Allocation & Capacity Booking Platform"
        "</p>",
        unsafe_allow_html=True
    )

    st.divider()

    c1, c2, c3 = st.columns([1,1.2,1])

    with c2:

        st.markdown("""
        <div class='section-box'>
        """, unsafe_allow_html=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button(
            "Login",
            use_container_width=True
        ):

            role = login_user(username, password)

            if role:

                st.session_state.logged_in = True
                st.session_state.role = role

                st.rerun()

            else:
                st.error("Invalid Credentials")

        st.markdown("""
        <br>

        <div class='small-text'>

        ✅ Real-Time Slot Allocation<br>
        ✅ Role-Based Access Control<br>
        ✅ Capacity Management System

        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ================= MAIN =================
role = st.session_state.get("role", "")

# ================= SIDEBAR =================
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Book Slots",
        "Execution Panel",
        "Slot Control"
    ]
)

st.sidebar.divider()

st.sidebar.success(f"👤 {str(role).upper()}")

if st.sidebar.button(
    "Logout",
    use_container_width=True
):

    st.session_state.clear()
    st.rerun()

# ================= DASHBOARD =================
if page == "Dashboard":

    from datetime import date

    st.title("📊 Dashboard")

    dashboard_date = st.date_input(
        "Dashboard Date",
        min_value=date.today()
    )

    dashboard_date_str = str(dashboard_date)

    booked, available, utilization = get_dashboard_stats_by_date(
        dashboard_date_str
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Booked Slots</div>
            <div class='metric-value'>{booked}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Available Slots</div>
            <div class='metric-value'>{available}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-title'>Utilization</div>
            <div class='metric-value'>{utilization}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if st.button(
        "Load Dashboard Data",
        use_container_width=True
    ):

        data = get_bookings_by_date(
            dashboard_date_str
        )

        df = pd.DataFrame(
            data,
            columns=[
                "Booking ID",
                "JR ID",
                "Client",
                "Date",
                "Slot"
            ]
        )

        if not df.empty:

            st.dataframe(
                df,
                use_container_width=True,
                height=500
            )

        else:
            st.info("No bookings found")
# ================= BOOKING =================
if page == "Book Slots" and role in ["sales", "admin"]:

    st.title("📝 Slot Booking")

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        jr_id = st.number_input(
            "JR ID",
            min_value=1
        )

    with c2:
        client = st.text_input("Client Name")

    from datetime import date

    date = st.date_input(
    "Booking Date",
    min_value=date.today()
)

    date_str = str(date)

    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("🎯 Available Slots")

    slots = get_available_slots(date_str)

    selected_slots = []

    cols = st.columns(4)

    for i, slot in enumerate(slots):

        with cols[i % 4]:

            st.markdown(f"""
            <div class='slot-card'>
                <div class='slot-title'>
                    SLOT {slot}
                </div>
            </div>
            """, unsafe_allow_html=True)

            checked = st.checkbox(
                f"Select",
                key=f"slot_{slot}"
            )

            if checked:
                selected_slots.append(slot)

    st.divider()

    if st.button(
        "🚀 Confirm Booking",
        use_container_width=True
    ):

        if selected_slots:

            ok, msg = book_with_limit(
                jr_id,
                client,
                date_str,
                selected_slots
            )

            if ok:

                st.success("✅ Booking Successful")
                st.rerun()

            else:
                st.error(msg)

        else:
            st.warning("Select at least one slot")

# ================= EXECUTION PANEL =================
if page == "Execution Panel" and role in ["execution", "admin"]:

    st.title("⚙️ Execution Panel")

    exec_date = st.date_input(
        "Select Date"
    )

    data = get_bookings_by_date(
        str(exec_date)
    )

    if not data:
        st.info("No bookings for selected date")

    for row in data:

        bid, jr, cname, d, s = row

        st.markdown(f"""
        <div class='section-box'>

        <h3>📌 Booking #{bid}</h3>

        👤 <b>Client:</b> {cname}<br><br>

        📅 <b>Date:</b> {d}<br><br>

        🎯 <b>Slot:</b> {s}

        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:

            new_date = st.date_input(
                "New Date",
                key=f"d{bid}"
            )

        with c2:

            new_slot = st.number_input(
                "New Slot",
                min_value=1,
                max_value=16,
                key=f"s{bid}"
            )

        with c3:

            st.write("")

            if st.button(
                "Update",
                key=f"u{bid}",
                use_container_width=True
            ):

                update_booking(
                    bid,
                    str(new_date),
                    new_slot
                )

                st.success("Updated")
                st.rerun()

            if st.button(
                "Delete",
                key=f"del{bid}",
                use_container_width=True
            ):

                delete_booking(bid)

                st.warning("Deleted")
                st.rerun()

# ================= SLOT CONTROL =================
if page == "Slot Control" and role in ["execution", "admin"]:

    st.title("🎯 Slot Control")

    st.markdown("<div class='section-box'>", unsafe_allow_html=True)

    config_date = st.date_input(
        "Select Date"
    )

    max_slots = st.slider(
        "Maximum Slots",
        1,
        16,
        8
    )

    st.write(f"### Allowed Slots: {max_slots}")

    if st.button(
        "Save Slot Limit",
        use_container_width=True
    ):

        set_max_slots(
            str(config_date),
            max_slots
        )

        st.success("✅ Slot Limit Updated")

    st.markdown("</div>", unsafe_allow_html=True)