from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import mysql.connector
import os

from dotenv import load_dotenv

from werkzeug.utils import secure_filename
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)

app.secret_key = "shopkart_secret_key_123"


# ============================================================
# DATABASE
# ============================================================

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE")
}


# ============================================================
# UPLOAD CONFIG
# ============================================================

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "static",
    "images"
)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# ============================================================
# FILE CHECK
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin():

    return (
        session.get("user_role")
        == "admin"
    )


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE is_active = 1
            ORDER BY id DESC
            """
        )

        products = cursor.fetchall()

        return render_template(
            "index.html",
            products=products
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# PRODUCTS
# ============================================================

@app.route("/products")
def products():

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE is_active = 1
            ORDER BY id DESC
            """
        )

        products = cursor.fetchall()

        return render_template(
            "products.html",
            products=products
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# PRODUCT DETAILS
# ============================================================

@app.route("/product/<int:product_id>")
def product_details(product_id):

    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE id = %s
            AND is_active = 1
            """,
            (product_id,)
        )

        product = cursor.fetchone()

        if not product:

            return "Product not found.", 404

        return render_template(
            "product.html",
            product=product
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# CART
# ============================================================

@app.route("/cart")
def cart():

    return render_template(
        "cart.html"
    )


# ============================================================
# CHECKOUT
# ============================================================

@app.route("/checkout")
def checkout():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return render_template(
        "checkout.html"
    )


# ============================================================
# REGISTER
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name or not email or not password:

            return render_template(
                "register.html",
                error="All fields are required."
            )


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            # ------------------------------------------------
            # CHECK EXISTING EMAIL
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing = cursor.fetchone()

            if existing:

                return render_template(
                    "register.html",
                    error="Email already registered."
                )


            # ------------------------------------------------
            # HASH PASSWORD
            # ------------------------------------------------

            hashed_password = generate_password_hash(
                password
            )


            # ------------------------------------------------
            # CREATE CUSTOMER
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'customer'
                )
                """,
                (
                    name,
                    email,
                    hashed_password
                )
            )

            connection.commit()


            return redirect(
                url_for("login")
            )


        except Exception as e:

            connection.rollback()

            return (
                "Registration error: "
                + str(e),
                500
            )


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            # ------------------------------------------------
            # FIND USER BY EMAIL
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()


            if not user:

                return render_template(
                    "login.html",
                    error="Invalid email or password."
                )


            stored_password = user["password"]

            password_valid = False


            # ------------------------------------------------
            # CHECK HASHED PASSWORD
            # ------------------------------------------------

            try:

                password_valid = check_password_hash(
                    stored_password,
                    password
                )

            except ValueError:

                password_valid = False


            # ------------------------------------------------
            # OLD PLAIN-TEXT PASSWORD SUPPORT
            # ------------------------------------------------

            if not password_valid:

                if stored_password == password:

                    password_valid = True


                    # ----------------------------------------
                    # AUTOMATICALLY HASH OLD PASSWORD
                    # ----------------------------------------

                    new_hashed_password = (
                        generate_password_hash(password)
                    )

                    cursor.execute(
                        """
                        UPDATE users
                        SET password = %s
                        WHERE id = %s
                        """,
                        (
                            new_hashed_password,
                            user["id"]
                        )
                    )

                    connection.commit()


            # ------------------------------------------------
            # LOGIN FAILED
            # ------------------------------------------------

            if not password_valid:

                return render_template(
                    "login.html",
                    error="Invalid email or password."
                )


            # ------------------------------------------------
            # SESSION
            # ------------------------------------------------

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]

            session["user_role"] = user["role"]


            # ------------------------------------------------
            # ADMIN
            # ------------------------------------------------

            if user["role"] == "admin":

                return redirect(
                    url_for("admin_dashboard")
                )


            # ------------------------------------------------
            # CUSTOMER
            # ------------------------------------------------

            return redirect(
                url_for("home")
            )


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# PLACE ORDER
# ============================================================

@app.route(
    "/place-order",
    methods=["POST"]
)
def place_order():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    customer_name = request.form.get(
        "customer_name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    address = request.form.get(
        "address",
        ""
    ).strip()

    city = request.form.get(
        "city",
        ""
    ).strip()

    pincode = request.form.get(
        "pincode",
        ""
    ).strip()

    payment_method = request.form.get(
        "payment_method",
        "COD"
    )


    product_ids = request.form.getlist(
        "product_id"
    )

    quantities = request.form.getlist(
        "quantity"
    )


    if not product_ids:

        return "Cart is empty.", 400


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        verified_items = []

        total = 0


        # ----------------------------------------------------
        # VERIFY PRODUCTS
        # ----------------------------------------------------

        for i in range(
            len(product_ids)
        ):

            product_id = int(
                product_ids[i]
            )

            quantity = int(
                quantities[i]
            )


            cursor.execute(
                """
                SELECT *
                FROM products
                WHERE id = %s
                AND is_active = 1
                """,
                (product_id,)
            )

            product = cursor.fetchone()


            if not product:

                raise Exception(
                    "Product is not available."
                )


            if product["stock"] < quantity:

                raise Exception(
                    f'Not enough stock for '
                    f'{product["name"]}.'
                )


            price = float(
                product["price"]
            )


            total += (
                price * quantity
            )


            verified_items.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "price": price
                }
            )


        # ----------------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO orders
            (
                customer_name,
                email,
                phone,
                address,
                city,
                pincode,
                payment_method,
                total_amount,
                order_status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Pending'
            )
            """,
            (
                customer_name,
                email,
                phone,
                address,
                city,
                pincode,
                payment_method,
                total
            )
        )


        order_id = cursor.lastrowid


        # ----------------------------------------------------
        # ORDER ITEMS + STOCK
        # ----------------------------------------------------

        for item in verified_items:

            cursor.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    product_id,
                    quantity,
                    price
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    order_id,
                    item["product_id"],
                    item["quantity"],
                    item["price"]
                )
            )


            cursor.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s
                """,
                (
                    item["quantity"],
                    item["product_id"]
                )
            )


        connection.commit()


        return redirect(
            url_for(
                "order_success",
                order_id=order_id
            )
        )


    except Exception as e:

        connection.rollback()

        return (
            "Order failed: "
            + str(e),
            500
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ORDER SUCCESS
# ============================================================

@app.route(
    "/order-success/<int:order_id>"
)
def order_success(order_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE id = %s
            """,
            (order_id,)
        )


        order = cursor.fetchone()


        if not order:

            return "Order not found.", 404


        return render_template(
            "order_success.html",
            order=order,
            order_id=order_id
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# MY ORDERS
# ============================================================

@app.route("/orders")
def orders():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT *
            FROM orders
            WHERE email = %s
            ORDER BY created_at DESC
            """,
            (
                session.get(
                    "user_email"
                ),
            )
        )


        orders_data = cursor.fetchall()


        for order in orders_data:

            cursor.execute(
                """
                SELECT
                    oi.*,
                    p.name AS product_name,
                    p.category AS product_category,
                    p.image AS product_image
                FROM order_items oi
                JOIN products p
                    ON oi.product_id = p.id
                WHERE oi.order_id = %s
                """,
                (
                    order["id"],
                )
            )


            order["items"] = (
                cursor.fetchall()
            )


        return render_template(
            "orders.html",
            orders=orders_data
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@app.route("/admin")
def admin_dashboard():

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        # ----------------------------------------------------
        # TOTAL ACTIVE PRODUCTS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM products
            WHERE is_active = 1
            """
        )

        total_products = (
            cursor.fetchone()["total"]
        )


        # ----------------------------------------------------
        # TOTAL CUSTOMERS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM users
            WHERE role = 'customer'
            """
        )

        total_customers = (
            cursor.fetchone()["total"]
        )


        # ----------------------------------------------------
        # TOTAL ORDERS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM orders
            """
        )

        total_orders = (
            cursor.fetchone()["total"]
        )


        # ----------------------------------------------------
        # TOTAL SALES
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                COALESCE(
                    SUM(total_amount),
                    0
                ) AS total
            FROM orders
            WHERE order_status != 'Cancelled'
            """
        )

        total_sales = (
            cursor.fetchone()["total"]
        )


        # ----------------------------------------------------
        # RECENT ORDERS
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                id,
                customer_name,
                email,
                total_amount,
                order_status,
                created_at
            FROM orders
            ORDER BY created_at DESC
            LIMIT 5
            """
        )

        recent_orders = (
            cursor.fetchall()
        )


        return render_template(
            "admin.html",
            total_products=total_products,
            total_customers=total_customers,
            total_orders=total_orders,
            total_sales=total_sales,
            recent_orders=recent_orders
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ADMIN PRODUCTS
# ============================================================

@app.route("/admin/products")
def admin_products():

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT *
            FROM products
            ORDER BY id DESC
            """
        )


        products_data = (
            cursor.fetchall()
        )


        return render_template(
            "admin_products.html",
            products=products_data
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ADD PRODUCT
# ============================================================

@app.route(
    "/admin/products/add",
    methods=["GET", "POST"]
)
def add_product():

    if not is_admin():

        return redirect(
            url_for("login")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        price = request.form.get(
            "price",
            "0"
        )

        category = request.form.get(
            "category",
            ""
        ).strip()

        stock = request.form.get(
            "stock",
            "0"
        )

        image = request.files.get(
            "image"
        )


        try:

            price = float(price)

            stock = int(stock)

        except ValueError:

            return render_template(
                "add_product.html",
                error="Invalid price or stock."
            )


        filename = ""


        if image and image.filename:

            if not allowed_file(
                image.filename
            ):

                return render_template(
                    "add_product.html",
                    error="Invalid image format."
                )


            filename = secure_filename(
                image.filename
            )


            base, extension = os.path.splitext(
                filename
            )


            counter = 1


            while os.path.exists(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            ):

                filename = (
                    f"{base}_{counter}{extension}"
                )

                counter += 1


            image.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )


        connection = get_db_connection()

        cursor = connection.cursor()


        try:

            cursor.execute(
                """
                INSERT INTO products
                (
                    name,
                    description,
                    price,
                    category,
                    stock,
                    image,
                    is_active
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    1
                )
                """,
                (
                    name,
                    description,
                    price,
                    category,
                    stock,
                    filename
                )
            )


            connection.commit()


            return redirect(
                url_for(
                    "admin_products"
                )
            )


        finally:

            cursor.close()
            connection.close()


    return render_template(
        "add_product.html"
    )


# ============================================================
# EDIT PRODUCT
# ============================================================

@app.route(
    "/admin/products/edit/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT *
            FROM products
            WHERE id = %s
            """,
            (product_id,)
        )


        product = cursor.fetchone()


        if not product:

            return "Product not found.", 404


        if request.method == "POST":

            name = request.form.get(
                "name",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            price = request.form.get(
                "price",
                "0"
            )

            category = request.form.get(
                "category",
                ""
            ).strip()

            stock = request.form.get(
                "stock",
                "0"
            )

            image = request.files.get(
                "image"
            )


            try:

                price = float(price)

                stock = int(stock)

            except ValueError:

                return render_template(
                    "edit_product.html",
                    product=product,
                    error="Invalid price or stock."
                )


            old_image = product["image"]

            new_image = old_image


            if image and image.filename:

                if not allowed_file(
                    image.filename
                ):

                    return render_template(
                        "edit_product.html",
                        product=product,
                        error="Invalid image format."
                    )


                new_image = secure_filename(
                    image.filename
                )


                base, extension = os.path.splitext(
                    new_image
                )


                counter = 1


                while os.path.exists(
                    os.path.join(
                        UPLOAD_FOLDER,
                        new_image
                    )
                ):

                    new_image = (
                        f"{base}_{counter}{extension}"
                    )

                    counter += 1


                image.save(
                    os.path.join(
                        UPLOAD_FOLDER,
                        new_image
                    )
                )


            cursor.execute(
                """
                UPDATE products
                SET
                    name = %s,
                    description = %s,
                    price = %s,
                    category = %s,
                    stock = %s,
                    image = %s
                WHERE id = %s
                """,
                (
                    name,
                    description,
                    price,
                    category,
                    stock,
                    new_image,
                    product_id
                )
            )


            connection.commit()


            return redirect(
                url_for(
                    "admin_products"
                )
            )


        return render_template(
            "edit_product.html",
            product=product
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# DEACTIVATE PRODUCT
# ============================================================

@app.route(
    "/admin/products/deactivate/<int:product_id>"
)
def deactivate_product(product_id):

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            UPDATE products
            SET is_active = 0
            WHERE id = %s
            """,
            (product_id,)
        )


        connection.commit()


        return redirect(
            url_for(
                "admin_products"
            )
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ACTIVATE PRODUCT
# ============================================================

@app.route(
    "/admin/products/activate/<int:product_id>"
)
def activate_product(product_id):

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            UPDATE products
            SET is_active = 1
            WHERE id = %s
            """,
            (product_id,)
        )


        connection.commit()


        return redirect(
            url_for(
                "admin_products"
            )
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# ADMIN ORDERS
# ============================================================

@app.route("/admin/orders")
def admin_orders():

    if not is_admin():

        return redirect(
            url_for("login")
        )


    connection = get_db_connection()

    cursor = connection.cursor(
        dictionary=True
    )


    try:

        cursor.execute(
            """
            SELECT *
            FROM orders
            ORDER BY created_at DESC
            """
        )


        orders_data = (
            cursor.fetchall()
        )


        for order in orders_data:

            cursor.execute(
                """
                SELECT
                    oi.*,
                    p.name,
                    p.category,
                    p.image
                FROM order_items oi
                JOIN products p
                    ON oi.product_id = p.id
                WHERE oi.order_id = %s
                """,
                (
                    order["id"],
                )
            )


            order["items"] = (
                cursor.fetchall()
            )


        return render_template(
            "admin_orders.html",
            orders=orders_data
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# UPDATE ORDER STATUS
# ============================================================

@app.route(
    "/admin/orders/update/<int:order_id>",
    methods=["POST"]
)
def update_order_status(order_id):

    if not is_admin():

        return redirect(
            url_for("login")
        )


    status = request.form.get(
        "order_status"
    )


    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Shipped",
        "Out for Delivery",
        "Delivered",
        "Cancelled"
    ]


    if status not in allowed_statuses:

        return "Invalid status.", 400


    connection = get_db_connection()

    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            UPDATE orders
            SET order_status = %s
            WHERE id = %s
            """,
            (
                status,
                order_id
            )
        )


        connection.commit()


        return redirect(
            url_for(
                "admin_orders"
            )
        )


    finally:

        cursor.close()
        connection.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )