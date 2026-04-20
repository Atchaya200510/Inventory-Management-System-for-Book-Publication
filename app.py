from flask import Flask, render_template, request, redirect, jsonify, session, url_for;

import sqlite3
import os


app = Flask(__name__)
app.secret_key = "inventory_secret_key"


DB_PATH = os.path.join(os.path.dirname(__file__), "database", "inventory.db")


def get_db_connection():

    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)

    conn.row_factory = sqlite3.Row
    return conn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'cover')


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- API ----------------

@app.route('/api/books', methods=['POST'])

def create_book():

    title = request.form.get('title')

    author = request.form.get('author')

    category = request.form.get('category')

    quantity = request.form.get('quantity', 0)

    price = request.form.get('price', 0)

    description = request.form.get('description')


    image = request.files.get('image')

    image_filename = "default.jpg"


    if image:

        image_filename = image.filename

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))


        conn = get_db_connection()

        conn.execute(
        '''

        INSERT INTO books (title, author, category, quantity, price, description, image_url)

        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',

        (title, author, category, quantity, price, description, image_filename)
        )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Book added successfully'})

@app.route('/api/books', methods=['GET'])

def get_books():

    conn = get_db_connection()

    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()


    book_list = [dict(book) for book in books]

    return jsonify(book_list)


@app.route('/api/books/<int:book_id>', methods=['GET'])

def get_book(book_id):

    conn = get_db_connection()

    book = conn.execute(

        "SELECT * FROM books WHERE id = ?", (book_id,)

    ).fetchone()
    conn.close()

    if book is None:

        return jsonify({'error': 'Book not found'}), 404


    return jsonify(dict(book))


from werkzeug.utils import secure_filename
import os


@app.route('/api/books/count', methods=['GET'])

def get_book_count():

    count = Book.query.count()

    return jsonify({"total_books": count})

@app.route('/api/books/<int:book_id>', methods=['PUT'])

def update_book(book_id):

    conn = get_db_connection()

    book = conn.execute(

        'SELECT * FROM books WHERE id = ?', (book_id,)

    ).fetchone()


    if book is None:
        conn.close()

        return jsonify({'error': 'Book not found'}), 404


    title = request.form.get('title')

    author = request.form.get('author')

    category = request.form.get('category')

    price = request.form.get('price')

    description = request.form.get('description')


    image = request.files.get('image')

    image_filename = book['image_url']


    if image:

        image_filename = image.filename

        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))


    conn.execute(
        '''

        UPDATE books

        SET title=?, author=?, category=?, price=?, description=?, image_url=?

        WHERE id=?
        ''',

        (title, author, category, price, description, image_filename, book_id)
    )

    conn.commit()
    conn.close()


    return jsonify({'message': 'Book updated successfully'})


@app.route('/api/books/<int:book_id>', methods=['DELETE'])

def delete_book(book_id):

    conn = get_db_connection()

    book = conn.execute(

        'SELECT * FROM books WHERE id = ?', (book_id,)

    ).fetchone()


    if book is None:
        conn.close()

        return jsonify({'error': 'Book not found'}), 404


    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()


    return jsonify({'message': 'Book deleted successfully'})


@app.route('/api/distributors')

def api_distributors():

    conn = get_db_connection()

    distributors = conn.execute("SELECT * FROM distributors").fetchall()
    conn.close()

    return jsonify([dict(d) for d in distributors])


@app.route('/api/bills')

def get_bills():

    conn = get_db_connection()
    cursor = conn.cursor()


    bills = cursor.execute("""

        SELECT 

            b.id AS bill_id,

            d.name AS distributor,
            b.date,

            SUM(bi.quantity * bi.price) AS total

        FROM bills b

        JOIN distributors d ON b.distributor_id = d.id

        JOIN bill_items bi ON b.id = bi.bill_id

        GROUP BY b.id

        ORDER BY b.date DESC

    """).fetchall()

    conn.close()

    return jsonify([dict(b) for b in bills])


@app.route('/api/sales_summary')

def sales_summary():

    conn = get_db_connection()
    cursor = conn.cursor()


    data = cursor.execute("""

        SELECT 

            DATE(b.date) as day,

            SUM(bi.quantity * bi.price) as total

        FROM bills b

        JOIN bill_items bi ON b.id = bi.bill_id

        GROUP BY DATE(b.date)

        ORDER BY day

    """).fetchall()

    conn.close()

    return jsonify([dict(d) for d in data])

@app.route('/book/<int:book_id>')

def book_details(book_id):

    conn = get_db_connection()

    book = conn.execute(

        "SELECT * FROM books WHERE id=?", (book_id,)

    ).fetchone()
    conn.close()


    if not book:

        return "Book not found", 404


    return render_template("book_details.html", book=book)

# ---------------- PAGES ----------------

@app.route('/')

def home():

    return render_template("index.html")

@app.route('/admin_login', methods=['GET','POST'])

def admin_login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']


        conn = get_db_connection()

        user = conn.execute(

            "SELECT * FROM admin WHERE username=? AND password=?",

            (username, password)

        ).fetchone()
        conn.close()

        if user:
            session['role'] = 'admin'
            return redirect('/admin_dashboard')


    return render_template("admin_login.html")

@app.route('/staff_login', methods=['GET','POST'])

def staff_login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']


        conn = get_db_connection()

        user = conn.execute(

            "SELECT * FROM staff WHERE username=? AND password=?",

            (username, password)

        ).fetchone()
        conn.close()


        if user:
            session['role'] = 'staff'
            return redirect('/staff_dashboard')


    return render_template("staff_login.html")


@app.route('/admin_dashboard')

def admin_dashboard():

    return render_template("admin_dashboard.html")


@app.route('/staff_dashboard')

def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect('/staff_login')

    return render_template("staff_dashboard.html")

# ---------------- VIEW BOOKS (ROLE BASED) ----------------

@app.route('/admin/view_books')
def admin_view_books():
    if session.get('role') != 'admin':
        return "Unauthorized", 403
    return render_template("admin_viewbooks.html")


@app.route('/staff/view_books')
def staff_view_books():
    if session.get('role') != 'staff':
        return "Unauthorized", 403
    return render_template("staff_viewbooks.html")



# ---------------- ADD BOOK ----------------

@app.route('/add_book', methods=['GET', 'POST'])

def add_book():

    if request.method == 'POST':

        title = request.form['title']

        author = request.form['author']

        category = request.form['category']

        quantity = int(request.form['quantity'])

        price = float(request.form['price'])

        image = request.files['image']

        if image and image.filename != "":
            cover_folder = os.path.join("static", "cover")
            os.makedirs(cover_folder, exist_ok=True)

            image_path = os.path.join(cover_folder, image.filename)
            image.save(image_path)

            image_url = image.filename
        else:
            image_url = ""

        conn = get_db_connection()
        cursor = conn.cursor()


        book = cursor.execute(

            "SELECT * FROM books WHERE title=?",
            (title,)

        ).fetchone()


        if book:

            new_qty = book['quantity'] + quantity

            cursor.execute(

                "UPDATE books SET quantity=?, author=?, category=?, price=?, image_url=? WHERE title=?",

                (new_qty, author, category, price, image_url, title)
            )

        else:

            cursor.execute(

                "INSERT INTO books (title, author, category, quantity, price, image_url) VALUES (?, ?, ?, ?, ?, ?)",

                (title, author, category, quantity, price, image_url)
            )

        conn.commit()
        conn.close()

        return redirect('/staff/view_books')

    return render_template("add_book.html")

@app.route('/staff/edit_book/<int:book_id>')

def edit_book(book_id):
    return render_template("edit_book.html", book_id=book_id)

@app.route('/logout')

def logout():

    return redirect('/')


@app.route('/stock_manage')

def stock_manage():

    return render_template("stock_manage.html")


@app.route('/update_stock', methods=['POST'])
def update_stock():
    data = request.get_json()

    book_id = int(data['book_id'])
    qty = int(data['quantity'])
    action = data['action']

    conn = get_db_connection()
    cursor = conn.cursor()

    book = cursor.execute(
        "SELECT quantity, price FROM books WHERE id=?",
        (book_id,)
    ).fetchone()

    if not book:
        conn.close()
        return jsonify({"message": "Book not found"})

    current_qty = book['quantity']

    # ---------- STOCK OUT ----------
    if action == 'out':
        distributor_id = int(data.get('distributor_id'))
        price = float(book['price'])

        if qty > current_qty:
            conn.close()
            return jsonify({"message": "Not enough stock available"})

        # 1️⃣ Create bill
        cursor.execute(
            "INSERT INTO bills (distributor_id) VALUES (?)",
            (distributor_id,)
        )
        bill_id = cursor.lastrowid

        # 2️⃣ Add bill item
        cursor.execute("""
            INSERT INTO bill_items (bill_id, book_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (bill_id, book_id, qty, price))

        # 3️⃣ Reduce stock
        cursor.execute("""
            UPDATE books SET quantity = quantity - ?
            WHERE id = ?
        """, (qty, book_id))

        conn.commit()
        conn.close()

        return jsonify({
            "message": "Stock out successful. Bill generated.",
            "bill_id": bill_id
        })

    # ---------- STOCK IN ----------
    else:
        new_qty = current_qty + qty

        cursor.execute(
            "UPDATE books SET quantity=? WHERE id=?",
            (new_qty, book_id)
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Stock added successfully"})

# ---------------- DISTRIBUTORS ----------------

@app.route('/staff_distributors')

def staff_distributors():
    if session.get('role') != 'staff':
        return "Unauthorized", 403

    return render_template("staff_distributors.html")


@app.route('/add_distributor', methods=['POST'])

def add_distributor():
    if session.get('role') != 'staff':
        return "Unauthorized", 403

    name = request.form['name']

    contact = request.form['contact']

    address = request.form['address']


    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(

        "INSERT INTO distributors (name, contact, address) VALUES (?, ?, ?)",
        (name, contact, address)
    )
    conn.commit()
    conn.close()

    return redirect('/staff_distributors')

@app.route('/admin_distributors')

def admin_distributors():
    if session.get('role') != 'admin':
        return "Unauthorized", 403

    return render_template("admin_distributors.html")

# ---------------- BILLING ----------------

@app.route('/billing')

def billing():

    return render_template("billing.html")
    
# ---------------- VIEW BILLS API ---------------

@app.route('/view_bills')

def view_bills():

    return render_template("view_bills.html")


from flask import send_file

from reportlab.lib.pagesizes import A4

from reportlab.pdfgen import canvas

from io import BytesIO


@app.route('/invoice/<int:bill_id>')

def generate_invoice(bill_id):

    conn = get_db_connection()
    cursor = conn.cursor()


    bill = cursor.execute("""

        SELECT b.id, b.date, d.name

        FROM bills b

        JOIN distributors d ON b.distributor_id = d.id

        WHERE b.id = ?

    """, (bill_id,)).fetchone()


    items = cursor.execute("""

        SELECT bk.title, bi.quantity, bi.price

        FROM bill_items bi

        JOIN books bk ON bi.book_id = bk.id

        WHERE bi.bill_id = ?

    """, (bill_id,)).fetchall()

    conn.close()


    if not bill:

        return "Bill not found", 404


    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4


    # ---- HEADER ----

    pdf.setFont("Helvetica-Bold", 18)

    pdf.drawString(50, height - 50, "INVOICE")


    pdf.setFont("Helvetica", 11)

    pdf.drawString(50, height - 90, f"Invoice No: {bill['id']}")

    pdf.drawString(50, height - 110, f"Date: {bill['date']}")

    pdf.drawString(50, height - 130, f"Distributor: {bill['name']}")


    # ---- TABLE HEADER ----

    y = height - 180

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(50, y, "Book")

    pdf.drawString(300, y, "Qty")

    pdf.drawString(350, y, "Price")

    pdf.drawString(430, y, "Total")


    pdf.line(50, y - 5, 550, y - 5)


    # ---- TABLE ROWS ----

    total_amount = 0

    pdf.setFont("Helvetica", 11)

    y -= 30


    for item in items:

        line_total = item["quantity"] * item["price"]

        total_amount += line_total


        pdf.drawString(50, y, item["title"])

        pdf.drawString(300, y, str(item["quantity"]))

        pdf.drawString(350, y, f"₹{item['price']}")

        pdf.drawString(430, y, f"₹{line_total}")

        y -= 25


    # ---- GRAND TOTAL ----

    pdf.setFont("Helvetica-Bold", 12)

    pdf.line(350, y, 550, y)

    y -= 30

    pdf.drawString(350, y, "Grand Total:")

    pdf.drawString(450, y, f"₹{total_amount}")


    pdf.showPage()

    pdf.save()


    buffer.seek(0)

    return send_file(
        buffer,

        as_attachment=True,

        download_name=f"Invoice_{bill_id}.pdf",

        mimetype='application/pdf'
    )

@app.route('/invoice_preview/<int:bill_id>')
def invoice_preview(bill_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    bill = cursor.execute("""
        SELECT b.id, b.date, d.name
        FROM bills b
        JOIN distributors d ON b.distributor_id = d.id
        WHERE b.id = ?
    """, (bill_id,)).fetchone()

    items = cursor.execute("""
        SELECT bk.title, bi.quantity, bi.price
        FROM bill_items bi
        JOIN books bk ON bi.book_id = bk.id
        WHERE bi.bill_id = ?
    """, (bill_id,)).fetchall()

    conn.close()

    if not bill:
        return "Bill not found", 404

    grand_total = 0
    for i in items:
        grand_total += i["quantity"] * i["price"]

    # 🔥 ADD THIS PART
    if session.get("role") == "admin":
        back_url = url_for("view_bills")
    elif session.get("role") == "staff":
        back_url = url_for("stock_manage")  # change if different
    else:
        return redirect(url_for("login"))

    return render_template(
        "invoice_preview.html",
        bill=bill,
        items=items,
        grand_total=grand_total,
        back_url=back_url   # 🔥 PASS IT HERE
    )   
    
@app.route('/api/invoice/<int:bill_id>')
def get_invoice_api(bill_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    bill = cursor.execute("""
        SELECT b.id, b.date, d.name
        FROM bills b
        JOIN distributors d ON b.distributor_id = d.id
        WHERE b.id = ?
    """, (bill_id,)).fetchone()

    items = cursor.execute("""
        SELECT bk.title, bi.quantity, bi.price
        FROM bill_items bi
        JOIN books bk ON bi.book_id = bk.id
        WHERE bi.bill_id = ?
    """, (bill_id,)).fetchall()

    conn.close()

    if not bill:
        return jsonify({"error": "Bill not found"}), 404

    return jsonify({
        "bill": dict(bill),
        "items": [dict(item) for item in items]
    })

@app.route('/reports')

def reports():

    return render_template("reports.html")

@app.route('/api/reports/sales')

def sales_report():

    conn = get_db_connection()

    data = conn.execute("""

        SELECT b.id, b.date, d.name,

               SUM(bi.quantity * bi.price) as total

        FROM bills b

        JOIN bill_items bi ON b.id = bi.bill_id

        JOIN distributors d ON b.distributor_id = d.id

        GROUP BY b.id

        ORDER BY b.date DESC

    """).fetchall()
    conn.close()

    return jsonify([dict(r) for r in data])


@app.route('/api/reports/stock')

def stock_report():

    conn = get_db_connection()

    data = conn.execute("""

        SELECT title, category, quantity, price

        FROM books

        ORDER BY quantity ASC

    """).fetchall()
    conn.close()

    return jsonify([dict(r) for r in data])

# ---------------- DASHBOARD STATS API ----------------

@app.route('/api/dashboard/stats')
def dashboard_stats():
    conn = get_db_connection()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    total_bills = conn.execute(
        "SELECT COUNT(*) FROM bills"
    ).fetchone()[0]

    total_sales = conn.execute(
        "SELECT IFNULL(SUM(quantity * price), 0) FROM bill_items"
    ).fetchone()[0]

    conn.close()

    return jsonify({
        "total_books": total_books,
        "total_bills": total_bills,
        "total_sales": total_sales
    })

@app.route('/api/best_sellers')
def best_sellers():
    conn = get_db_connection()

    data = conn.execute("""
        SELECT books.title, SUM(bill_items.quantity) as total_sold
        FROM bill_items
        JOIN books ON bill_items.book_id = books.id
        GROUP BY books.id
        ORDER BY total_sold DESC
        LIMIT 5
    """).fetchall()

    conn.close()

    return jsonify([
        {"title": row["title"], "total_sold": row["total_sold"]}
        for row in data
    ])

if __name__ == "__main__":

    app.run(debug=True)
