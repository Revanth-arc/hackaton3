import sqlite3

DB_PATH = "firstruct.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_complaints():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM firs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_complaint_by_id(fir_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get main record
    cursor.execute("SELECT * FROM firs WHERE id = ?", (fir_id,))
    main_row = cursor.fetchone()
    if not main_row:
        conn.close()
        return None

    data = dict(main_row)

    # Get relations
    cursor.execute("SELECT vehicle_number FROM vehicles WHERE fir_id = ?", (fir_id,))
    data["vehicles"] = [r["vehicle_number"] for r in cursor.fetchall()]

    cursor.execute("SELECT weapon_type FROM weapons WHERE fir_id = ?", (fir_id,))
    data["weapons"] = [r["weapon_type"] for r in cursor.fetchall()]

    cursor.execute("SELECT item_description FROM stolen_items WHERE fir_id = ?", (fir_id,))
    data["stolen_items"] = [r["item_description"] for r in cursor.fetchall()]

    cursor.execute("SELECT section_code FROM ipc_sections WHERE fir_id = ?", (fir_id,))
    data["ipc_sections"] = [r["section_code"] for r in cursor.fetchall()]

    conn.close()
    return data


def get_complaint_by_hash(file_hash):
    """Retrieve complaint using file hash to avoid duplicates."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM firs WHERE file_hash = ? LIMIT 1", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return get_complaint_by_id(row["id"])
    return None


def search_complaints(query, filters=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query_str = f"%{query}%"

    sql = """
        SELECT DISTINCT f.* FROM firs f
        LEFT JOIN vehicles v ON f.id = v.fir_id
        WHERE (
            f.complaint_id LIKE ? OR
            f.victim_name LIKE ? OR
            f.accused_name LIKE ? OR
            f.crime_type LIKE ? OR
            f.location LIKE ? OR
            f.summary LIKE ? OR
            v.vehicle_number LIKE ?
        )
    """
    params = [query_str] * 7

    if filters:
        if filters.get("crime_type") and filters["crime_type"] != "All":
            sql += " AND f.crime_type = ?"
            params.append(filters["crime_type"])
        if filters.get("status") and filters["status"] != "All":
            sql += " AND f.status = ?"
            params.append(filters["status"])

    sql += " ORDER BY f.created_at DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_complaint(fir_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Let's delete from related tables first
    cursor.execute("DELETE FROM vehicles WHERE fir_id = ?", (fir_id,))
    cursor.execute("DELETE FROM weapons WHERE fir_id = ?", (fir_id,))
    cursor.execute("DELETE FROM stolen_items WHERE fir_id = ?", (fir_id,))
    cursor.execute("DELETE FROM ipc_sections WHERE fir_id = ?", (fir_id,))

    # Delete main record
    cursor.execute("DELETE FROM firs WHERE id = ?", (fir_id,))

    conn.commit()
    conn.close()

    # Optional: also delete cached files in exports/ directory if they exist
    # (assuming complaint_id was used, but we only have fir_id)
    # We will let the service handle file deletions if needed.
    return True


def get_statistics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM firs")
    total = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) as count FROM firs WHERE DATE(created_at) = DATE('now')")
    today = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(DISTINCT crime_type) as count FROM firs")
    unique_crimes = cursor.fetchone()["count"]

    cursor.execute(
        "SELECT crime_type, COUNT(*) as count FROM firs GROUP BY crime_type ORDER BY count DESC LIMIT 1"
    )
    top_crime_row = cursor.fetchone()
    top_crime = top_crime_row["crime_type"] if top_crime_row else "N/A"

    cursor.execute(
        "SELECT location, COUNT(*) as count FROM firs GROUP BY location ORDER BY count DESC LIMIT 1"
    )
    top_location_row = cursor.fetchone()
    top_location = top_location_row["location"] if top_location_row else "N/A"

    conn.close()
    return {
        "total": total,
        "today": today,
        "unique_crimes": unique_crimes,
        "top_crime": top_crime,
        "top_location": top_location,
    }
