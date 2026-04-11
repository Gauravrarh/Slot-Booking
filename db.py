from supabase import create_client

# 🔑 ADD HERE
SUPABASE_URL = "https://seqaakxtyzkwbhcpnlyk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlcWFha3h0eXprd2JoY3BubHlrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU4ODU4NDgsImV4cCI6MjA5MTQ2MTg0OH0.2R9jzBY8uxlVDhMf7wF4l-39PUaW9nFsU5MbQPu7ZHA"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ================= LOGIN =================
def login_user(username, password):
    res = supabase.table("users") \
        .select("role") \
        .eq("username", username) \
        .eq("password", password) \
        .execute()

    return res.data[0]["role"] if res.data else None


# ================= SLOT LIMIT =================
def get_max_slots(date):
    res = supabase.table("slot_config") \
        .select("max_slots") \
        .eq("slot_date", date) \
        .execute()

    return res.data[0]["max_slots"] if res.data else 8


def set_max_slots(date, max_slots):
    supabase.table("slot_config").upsert({
        "slot_date": date,
        "max_slots": max_slots
    }).execute()


# ================= JR HANDLING =================
def ensure_jr_exists(jr_id, client_name, salesperson_name):
    res = supabase.table("jr_master") \
        .select("jr_id") \
        .eq("jr_id", jr_id) \
        .execute()

    if not res.data:
        supabase.table("jr_master").insert({
            "jr_id": jr_id,
            "client_name": client_name,
            "salesperson_name": salesperson_name
        }).execute()


# ================= SLOT INVENTORY =================
def ensure_slots_exist(date):
    res = supabase.table("slot_inventory") \
        .select("slot_id") \
        .eq("slot_date", date) \
        .execute()

    if not res.data:
        for i in range(1, 41):
            supabase.table("slot_inventory").insert({
                "slot_date": date,
                "slot_number": i
            }).execute()


# ================= AVAILABLE SLOTS =================
def get_available_slots(date):
    ensure_slots_exist(date)

    max_slots = get_max_slots(date)

    booked = supabase.table("slot_bookings") \
        .select("slot_number") \
        .eq("slot_date", date) \
        .execute()

    booked_slots = [b["slot_number"] for b in booked.data]

    available = [
        i for i in range(1, max_slots + 1)
        if i not in booked_slots
    ]

    return available


# ================= BOOKING =================
def book_with_limit(jr_id, client_name, salesperson_name, date, slot_list):
    max_slots = get_max_slots(date)

    res = supabase.table("slot_bookings") \
        .select("slot_number") \
        .eq("slot_date", date) \
        .execute()

    current = len(res.data)

    if current + len(slot_list) > max_slots:
        return False, "Slot limit exceeded"

    try:
        # ✅ Ensure JR exists
        ensure_jr_exists(jr_id, client_name, salesperson_name)

        for slot in slot_list:
            supabase.table("slot_bookings").insert({
                "jr_id": jr_id,
                "client_name": client_name,
                "slot_date": date,
                "slot_number": slot
            }).execute()

        return True, "Booking successful"

    except Exception as e:
        return False, str(e)


# ================= BOOKINGS =================
def get_all_bookings():
    res = supabase.table("slot_bookings") \
        .select("*") \
        .order("slot_date") \
        .execute()

    return res.data


def delete_booking(booking_id):
    supabase.table("slot_bookings") \
        .delete() \
        .eq("booking_id", booking_id) \
        .execute()


def update_booking(booking_id, new_date, new_slot):
    supabase.table("slot_bookings") \
        .update({
            "slot_date": new_date,
            "slot_number": new_slot
        }) \
        .eq("booking_id", booking_id) \
        .execute()