import mysql.connector


# ================= CONNECTION =================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@123",   # CHANGE PASSWORD
        database="slot_booking_system",
        autocommit=True
    )


# ================= LOGIN =================
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username = %s AND password = %s",
        (username, password)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None


# ================= SLOT LIMIT =================
def get_max_slots(date):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT max_slots FROM slot_config WHERE slot_date = %s",
        (date,)
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else 8


def set_max_slots(date, max_slots):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO slot_config (slot_date, max_slots)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE max_slots = %s
    """, (date, max_slots, max_slots))

    conn.commit()

    cursor.close()
    conn.close()


# ================= SLOT INVENTORY =================
def ensure_slots_exist(date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM slot_inventory WHERE slot_date = %s",
        (date,)
    )

    count = cursor.fetchone()[0]

    if count == 0:

        for i in range(1, 17):

            cursor.execute(
                "INSERT INTO slot_inventory (slot_date, slot_number) VALUES (%s, %s)",
                (date, i)
            )

        conn.commit()

    cursor.close()
    conn.close()


def get_available_slots(date):

    ensure_slots_exist(date)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.slot_number
        FROM slot_inventory s
        LEFT JOIN slot_bookings b
        ON s.slot_date = b.slot_date
        AND s.slot_number = b.slot_number
        WHERE s.slot_date = %s
        AND b.slot_number IS NULL
        ORDER BY s.slot_number
    """, (date,))

    result = [r[0] for r in cursor.fetchall()]

    cursor.close()
    conn.close()

    return result


# ================= BOOKING =================
def book_with_limit(jr_id, client_name, date, slot_list):

    conn = get_connection()
    conn.autocommit = False

    cursor = conn.cursor()

    try:

        max_slots = get_max_slots(date)

        cursor.execute(
            "SELECT COUNT(*) FROM slot_bookings WHERE slot_date = %s",
            (date,)
        )

        current = cursor.fetchone()[0]

        if current + len(slot_list) > max_slots:
            return False, "Slot limit exceeded"

        query = """
        INSERT INTO slot_bookings
        (jr_id, client_name, slot_date, slot_number)
        VALUES (%s, %s, %s, %s)
        """

        for slot in slot_list:

            cursor.execute(
                query,
                (jr_id, client_name, date, slot)
            )

        conn.commit()

        return True, "Success"

    except Exception as e:

        conn.rollback()

        return False, str(e)

    finally:

        cursor.close()
        conn.close()


# ================= BOOKINGS =================
def get_bookings_by_date(date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT booking_id, jr_id, client_name,
               slot_date, slot_number
        FROM slot_bookings
        WHERE slot_date = %s
        ORDER BY slot_number
    """, (date,))

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


def get_all_bookings():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT booking_id, jr_id, client_name,
               slot_date, slot_number
        FROM slot_bookings
        ORDER BY slot_date
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return result


# ================= DASHBOARD =================
def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM slot_bookings")

    booked = cursor.fetchone()[0]

    available = max(0, 16 - booked)

    utilization = round((booked / 16) * 100, 1) if booked else 0

    cursor.close()
    conn.close()

    return booked, available, utilization


# ================= EDIT / DELETE =================
def delete_booking(booking_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM slot_bookings WHERE booking_id = %s",
        (booking_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()


def update_booking(booking_id, new_date, new_slot):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE slot_bookings
        SET slot_date = %s,
            slot_number = %s
        WHERE booking_id = %s
    """, (new_date, new_slot, booking_id))

    conn.commit()

    cursor.close()
    conn.close()