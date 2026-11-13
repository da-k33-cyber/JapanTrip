from flask import Flask, request, redirect, url_for, render_template_string, flash
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "japan-trip-local-secret"

DB_NAME = "japan_trip.db"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS days (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_date TEXT NOT NULL,
            city TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT DEFAULT ''
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_id INTEGER NOT NULL,
            activity_time TEXT DEFAULT '',
            title TEXT NOT NULL,
            location TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            map_url TEXT DEFAULT '',
            FOREIGN KEY(day_id) REFERENCES days(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ---------------- DESIGN ----------------

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Japan Trip Planner</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: 'Cairo', sans-serif;
    background: #f4f5f8;
    color: #202333;
}

header {
    background: linear-gradient(135deg, #171b35, #333d68);
    color: white;
    padding: 35px 20px;
    text-align: center;
}

header h1 {
    margin: 0;
    font-size: 32px;
}

header p {
    color: #d6d9e8;
}

.container {
    max-width: 1050px;
    margin: 30px auto;
    padding: 0 18px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}

.stat, .card, .day-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 3px 15px #00000008;
}

.stat {
    text-align: center;
}

.stat strong {
    display: block;
    font-size: 25px;
    color: #354477;
}

h2 {
    font-size: 21px;
}

input, textarea, select {
    width: 100%;
    padding: 12px;
    margin: 7px 0 13px;
    border: 1px solid #dfe2eb;
    border-radius: 9px;
    font-family: inherit;
    font-size: 14px;
    background: white;
}

textarea {
    resize: vertical;
    min-height: 65px;
}

button, .button {
    border: none;
    background: #354477;
    color: white;
    padding: 11px 18px;
    border-radius: 9px;
    cursor: pointer;
    font-family: inherit;
    font-size: 14px;
    text-decoration: none;
    display: inline-block;
}

button:hover, .button:hover {
    background: #222e58;
}

.delete {
    background: #c94b58;
}

.delete:hover {
    background: #a83240;
}

.secondary {
    background: #e9ecf5;
    color: #303c68;
}

.day-card {
    margin-bottom: 22px;
    border-right: 5px solid #354477;
}

.day-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.city {
    color: #52649b;
    font-weight: bold;
}

.activity {
    background: #f6f7fa;
    border-radius: 10px;
    padding: 14px;
    margin: 12px 0;
}

.activity h4 {
    margin: 0 0 7px;
}

.activity p {
    margin: 5px 0;
    font-size: 14px;
    color: #626779;
}

.activity a {
    color: #354477;
}

form.inline {
    display: inline;
}

.add-activity {
    border-top: 1px solid #eee;
    margin-top: 18px;
    padding-top: 12px;
}

label {
    font-weight: 700;
    font-size: 13px;
}

.flash {
    background: #e2f5e9;
    color: #21683c;
    padding: 12px;
    border-radius: 9px;
    margin-bottom: 15px;
}

.empty {
    text-align: center;
    color: #888;
    padding: 30px;
}

footer {
    text-align: center;
    color: #888;
    padding: 30px;
    font-size: 13px;
}

@media(max-width: 600px) {
    header h1 { font-size: 24px; }
    .stats { grid-template-columns: 1fr; }
    .container { margin-top: 18px; }
}
</style>
</head>

<body>

<header>
    <h1>🇯🇵 Japan Trip Planner</h1>
    <p>Our Group Trip • January 2027</p>
    <p>6 Friends · One Adventure</p>
</header>

<div class="container">

    {% with messages = get_flashed_messages() %}
      {% for message in messages %}
        <div class="flash">{{ message }}</div>
      {% endfor %}
    {% endwith %}

    <div class="stats">
        <div class="stat">
            <strong>{{ days|length }}</strong>
            أيام الرحلة
        </div>
        <div class="stat">
            <strong>{{ cities|length }}</strong>
            المدن
        </div>
        <div class="stat">
            <strong>{{ total_activities }}</strong>
            الفعاليات
        </div>
    </div>

    <div class="card">
        <h2>＋ إضافة يوم جديد</h2>

        <form action="{{ url_for('add_day') }}" method="POST">

            <label>التاريخ</label>
            <input type="date" name="trip_date" required>

            <label>المدينة</label>
            <input type="text" name="city"
                   placeholder="مثلاً: Tokyo" required>

            <label>عنوان اليوم</label>
            <input type="text" name="title"
                   placeholder="مثلاً: زيارة ديزني لاند" required>

            <label>وصف اليوم</label>
            <textarea name="description"
                      placeholder="اكتب تفاصيل اليوم..."></textarea>

            <button type="submit">إضافة اليوم</button>
        </form>
    </div>

    <h2 style="margin-top:35px">📅 جدول رحلتنا</h2>

    {% if days %}

        {% for day in days %}

        <div class="day-card">

            <div class="day-top">
                <div>
                    <div class="city">📍 {{ day.city }}</div>
                    <h2>{{ day.title }}</h2>
                    <small>📆 {{ day.trip_date }}</small>
                </div>

                <form class="inline"
                      action="{{ url_for('delete_day', day_id=day.id) }}"
                      method="POST"
                      onsubmit="return confirm('متأكد من حذف هذا اليوم وكل فعالياته؟')">
                    <button class="delete">حذف اليوم</button>
                </form>
            </div>

            {% if day.description %}
                <p>{{ day.description }}</p>
            {% endif %}

            <details>
                <summary style="cursor:pointer;color:#354477">
                    ✏️ تعديل بيانات اليوم
                </summary>

                <form action="{{ url_for('edit_day', day_id=day.id) }}"
                      method="POST">

                    <label>التاريخ</label>
                    <input type="date" name="trip_date"
                           value="{{ day.trip_date }}" required>

                    <label>المدينة</label>
                    <input name="city" value="{{ day.city }}" required>

                    <label>عنوان اليوم</label>
                    <input name="title" value="{{ day.title }}" required>

                    <label>الوصف</label>
                    <textarea name="description">{{ day.description }}</textarea>

                    <button type="submit">حفظ التعديلات</button>
                </form>
            </details>

            <div class="add-activity">
                <h3>🎯 الفعاليات</h3>

                {% for activity in day.activities %}

                    <div class="activity">

                        <h4>
                            {% if activity.activity_time %}
                                🕒 {{ activity.activity_time }} -
                            {% endif %}
                            {{ activity.title }}
                        </h4>

                        {% if activity.location %}
                            <p>📍 {{ activity.location }}</p>
                        {% endif %}

                        {% if activity.notes %}
                            <p>{{ activity.notes }}</p>
                        {% endif %}

                        {% if activity.map_url %}
                            <a href="{{ activity.map_url }}"
                               target="_blank" rel="noopener noreferrer">
                                فتح الموقع على Google Maps
                            </a>
                        {% endif %}

                        <details>
                            <summary style="cursor:pointer;margin-top:10px">
                                تعديل الفعالية
                            </summary>

                            <form action="{{ url_for('edit_activity', activity_id=activity.id) }}"
                                  method="POST">

                                <label>الوقت</label>
                                <input type="time" name="activity_time"
                                       value="{{ activity.activity_time }}">

                                <label>اسم الفعالية</label>
                                <input name="title"
                                       value="{{ activity.title }}" required>

                                <label>الموقع</label>
                                <input name="location"
                                       value="{{ activity.location }}">

                                <label>رابط الخريطة</label>
                                <input type="url" name="map_url"
                                       value="{{ activity.map_url }}">

                                <label>ملاحظات</label>
                                <textarea name="notes">{{ activity.notes }}</textarea>

                                <button type="submit">حفظ التعديل</button>
                            </form>
                        </details>

                        <form class="inline"
                              action="{{ url_for('delete_activity', activity_id=activity.id) }}"
                              method="POST"
                              onsubmit="return confirm('حذف الفعالية؟')">
                            <button class="delete">حذف الفعالية</button>
                        </form>

                    </div>

                {% else %}
                    <p class="empty">ما أضفتوا فعاليات لهذا اليوم بعد.</p>
                {% endfor %}

                <details>
                    <summary style="cursor:pointer;color:#354477;font-weight:bold">
                        ＋ إضافة فعالية جديدة
                    </summary>

                    <form action="{{ url_for('add_activity', day_id=day.id) }}"
                          method="POST">

                        <label>وقت الفعالية</label>
                        <input type="time" name="activity_time">

                        <label>اسم الفعالية</label>
                        <input name="title"
                               placeholder="مثلاً: Tokyo Disneyland" required>

                        <label>الموقع</label>
                        <input name="location"
                               placeholder="اسم المكان">

                        <label>رابط Google Maps</label>
                        <input type="url" name="map_url"
                               placeholder="https://maps.google.com/...">

                        <label>ملاحظات</label>
                        <textarea name="notes"
                                  placeholder="تفاصيل إضافية..."></textarea>

                        <button type="submit">إضافة الفعالية</button>
                    </form>
                </details>
            </div>

        </div>

        {% endfor %}

    {% else %}
        <div class="card empty">
            <h3>لسه ما فيه أيام في جدولكم!</h3>
            <p>ابدأ بإضافة أول يوم من رحلتكم.</p>
        </div>
    {% endif %}

</div>

<footer>
    Made with Python ❤️ · Japan Trip 2027
</footer>

</body>
</html>
"""


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():
    conn = get_db()

    days = conn.execute("""
        SELECT * FROM days
        ORDER BY trip_date, id
    """).fetchall()

    result = []

    for day in days:
        activities = conn.execute("""
            SELECT * FROM activities
            WHERE day_id = ?
            ORDER BY activity_time, id
        """, (day["id"],)).fetchall()

        result.append({
            **dict(day),
            "activities": activities
        })

    total_activities = conn.execute(
        "SELECT COUNT(*) FROM activities"
    ).fetchone()[0]

    cities = conn.execute(
        "SELECT DISTINCT city FROM days"
    ).fetchall()

    conn.close()

    return render_template_string(
        HTML,
        days=result,
        cities=cities,
        total_activities=total_activities
    )


# ---------------- DAYS ----------------

@app.route("/add_day", methods=["POST"])
def add_day():
    trip_date = request.form.get("trip_date", "").strip()
    city = request.form.get("city", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not trip_date or not city or not title:
        flash("فضلاً أكمل البيانات المطلوبة.")
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute("""
        INSERT INTO days (trip_date, city, title, description)
        VALUES (?, ?, ?, ?)
    """, (trip_date, city, title, description))

    conn.commit()
    conn.close()

    flash("تمت إضافة اليوم بنجاح!")
    return redirect(url_for("home"))


@app.route("/edit_day/<int:day_id>", methods=["POST"])
def edit_day(day_id):
    trip_date = request.form.get("trip_date", "").strip()
    city = request.form.get("city", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not trip_date or not city or not title:
        flash("فضلاً أكمل البيانات المطلوبة.")
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute("""
        UPDATE days
        SET trip_date=?, city=?, title=?, description=?
        WHERE id=?
    """, (trip_date, city, title, description, day_id))

    conn.commit()
    conn.close()

    flash("تم تعديل اليوم!")
    return redirect(url_for("home"))


@app.route("/delete_day/<int:day_id>", methods=["POST"])
def delete_day(day_id):
    conn = get_db()
    conn.execute("DELETE FROM days WHERE id=?", (day_id,))
    conn.commit()
    conn.close()

    flash("تم حذف اليوم.")
    return redirect(url_for("home"))


# ---------------- ACTIVITIES ----------------

@app.route("/add_activity/<int:day_id>", methods=["POST"])
def add_activity(day_id):
    activity_time = request.form.get("activity_time", "").strip()
    title = request.form.get("title", "").strip()
    location = request.form.get("location", "").strip()
    notes = request.form.get("notes", "").strip()
    map_url = request.form.get("map_url", "").strip()

    if not title:
        flash("اكتب اسم الفعالية.")
        return redirect(url_for("home"))

    conn = get_db()

    day = conn.execute(
        "SELECT id FROM days WHERE id=?", (day_id,)
    ).fetchone()

    if day is None:
        conn.close()
        flash("اليوم غير موجود.")
        return redirect(url_for("home"))

    conn.execute("""
        INSERT INTO activities
        (day_id, activity_time, title, location, notes, map_url)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (day_id, activity_time, title, location, notes, map_url))

    conn.commit()
    conn.close()

    flash("تمت إضافة الفعالية!")
    return redirect(url_for("home"))


@app.route("/edit_activity/<int:activity_id>", methods=["POST"])
def edit_activity(activity_id):
    activity_time = request.form.get("activity_time", "").strip()
    title = request.form.get("title", "").strip()
    location = request.form.get("location", "").strip()
    notes = request.form.get("notes", "").strip()
    map_url = request.form.get("map_url", "").strip()

    if not title:
        flash("اكتب اسم الفعالية.")
        return redirect(url_for("home"))

    conn = get_db()
    conn.execute("""
        UPDATE activities
        SET activity_time=?, title=?, location=?, notes=?, map_url=?
        WHERE id=?
    """, (activity_time, title, location, notes, map_url, activity_id))

    conn.commit()
    conn.close()

    flash("تم تعديل الفعالية!")
    return redirect(url_for("home"))


@app.route("/delete_activity/<int:activity_id>", methods=["POST"])
def delete_activity(activity_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM activities WHERE id=?", (activity_id,)
    )
    conn.commit()
    conn.close()

    flash("تم حذف الفعالية.")
    return redirect(url_for("home"))


# ---------------- START ----------------

if __name__ == "__main__":
    init_db()

    print("=" * 45)
    print("Japan Trip Planner is running!")
    print("Open your browser at: http://127.0.0.1:5000")
    print("=" * 45)

    app.run(host="127.0.0.1", port=5000, debug=False)
