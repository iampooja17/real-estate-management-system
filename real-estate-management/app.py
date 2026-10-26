from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "real_estate_secret_key"


# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Bananatree@517",
        database="real_estate"
    )


# -------------------------------------------------
# LOGIN
# -------------------------------------------------

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():

    username = request.form["username"]
    password = request.form["password"]

    if username == "admin" and password == "admin123":
        session["username"] = username
        return redirect("/dashboard")

    return "Invalid username or password"


# -------------------------------------------------
# LOGOUT
# -------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Total properties
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM properties
    """)
    total_properties = cursor.fetchone()["total"]

    # Available properties
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM properties
        WHERE status = 'Available'
    """)
    available_properties = cursor.fetchone()["total"]

    # Sold properties
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM properties
        WHERE status = 'Sold'
    """)
    sold_properties = cursor.fetchone()["total"]

    # Pending properties
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM properties
        WHERE status = 'Pending'
    """)
    pending_properties = cursor.fetchone()["total"]

    # Total customers
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM customers
    """)
    total_customers = cursor.fetchone()["total"]

    # Total agents
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM agents
    """)
    total_agents = cursor.fetchone()["total"]

    # Total transactions
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM transactions
    """)
    total_transactions = cursor.fetchone()["total"]

    # Total sales
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
    """)
    total_sales = cursor.fetchone()["total"]

    # Recent transactions
    cursor.execute("""
        SELECT
            t.transaction_id,
            c.name AS customer_name,
            p.property_type,
            p.location,
            t.amount,
            t.transaction_date
        FROM transactions t
        JOIN customers c
            ON t.customer_id = c.customer_id
        JOIN properties p
            ON t.property_id = p.property_id
        ORDER BY t.transaction_id DESC
        LIMIT 5
    """)

    recent_transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        total_properties=total_properties,
        available_properties=available_properties,
        sold_properties=sold_properties,
        pending_properties=pending_properties,
        total_customers=total_customers,
        total_agents=total_agents,
        total_transactions=total_transactions,
        total_sales=total_sales,
        recent_transactions=recent_transactions
    )


# -------------------------------------------------
# PROPERTIES
# -------------------------------------------------

@app.route("/properties")
def properties():

    if "username" not in session:
        return redirect("/")

    search = request.args.get("search", "")
    status = request.args.get("status", "")
    property_type = request.args.get("property_type", "")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            p.property_id,
            p.property_type,
            p.location,
            p.price,
            p.status,
            p.agent_id,
            a.name AS agent_name
        FROM properties p
        LEFT JOIN agents a
            ON p.agent_id = a.agent_id
        WHERE 1 = 1
    """

    values = []

    # Search
    if search:
        query += """
            AND (
                p.property_type LIKE %s
                OR p.location LIKE %s
            )
        """

        values.append("%" + search + "%")
        values.append("%" + search + "%")

    # Status filter
    if status:
        query += """
            AND p.status = %s
        """

        values.append(status)

    # Property type filter
    if property_type:
        query += """
            AND p.property_type = %s
        """

        values.append(property_type)

    query += """
        ORDER BY p.property_id DESC
    """

    cursor.execute(query, values)

    properties = cursor.fetchall()

    # Get agents
    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY name
    """)

    agents = cursor.fetchall()

    # Get property types
    cursor.execute("""
        SELECT DISTINCT property_type
        FROM properties
        ORDER BY property_type
    """)

    property_types = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "properties.html",
        properties=properties,
        agents=agents,
        property_types=property_types,
        search=search,
        status=status,
        property_type=property_type
    )


# -------------------------------------------------
# ADD PROPERTY
# -------------------------------------------------

@app.route("/add_property", methods=["POST"])
def add_property():

    if "username" not in session:
        return redirect("/")

    property_type = request.form["property_type"]
    location = request.form["location"]
    price = request.form["price"]
    status = request.form["status"]
    agent_id = request.form["agent_id"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO properties
        (
            property_type,
            location,
            price,
            status,
            agent_id
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        property_type,
        location,
        price,
        status,
        agent_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/properties")


# -------------------------------------------------
# EDIT PROPERTY
# -------------------------------------------------

@app.route("/edit_property/<int:property_id>")
def edit_property(property_id):

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM properties
        WHERE property_id = %s
    """, (property_id,))

    property_data = cursor.fetchone()

    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY name
    """)

    agents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_property.html",
        property=property_data,
        agents=agents
    )


# -------------------------------------------------
# UPDATE PROPERTY
# -------------------------------------------------

@app.route("/update_property/<int:property_id>", methods=["POST"])
def update_property(property_id):

    if "username" not in session:
        return redirect("/")

    property_type = request.form["property_type"]
    location = request.form["location"]
    price = request.form["price"]
    status = request.form["status"]
    agent_id = request.form["agent_id"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE properties
        SET
            property_type = %s,
            location = %s,
            price = %s,
            status = %s,
            agent_id = %s
        WHERE property_id = %s
    """, (
        property_type,
        location,
        price,
        status,
        agent_id,
        property_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/properties")


# -------------------------------------------------
# DELETE PROPERTY
# -------------------------------------------------

@app.route("/delete_property/<int:property_id>")
def delete_property(property_id):

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM properties
            WHERE property_id = %s
        """, (property_id,))

        connection.commit()

    except mysql.connector.Error as error:

        connection.rollback()

        cursor.close()
        connection.close()

        return f"Cannot delete property because it is connected to another record.<br><br>{error}"

    cursor.close()
    connection.close()

    return redirect("/properties")


# -------------------------------------------------
# CUSTOMERS
# -------------------------------------------------

@app.route("/customers")
def customers():

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY customer_id DESC
    """)

    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "customers.html",
        customers=customers
    )


# -------------------------------------------------
# ADD CUSTOMER
# -------------------------------------------------

@app.route("/add_customer", methods=["POST"])
def add_customer():

    if "username" not in session:
        return redirect("/")

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
        (
            name,
            phone,
            email
        )
        VALUES (%s, %s, %s)
    """, (
        name,
        phone,
        email
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/customers")


# -------------------------------------------------
# EDIT CUSTOMER
# -------------------------------------------------

@app.route("/edit_customer/<int:customer_id>")
def edit_customer(customer_id):

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM customers
        WHERE customer_id = %s
    """, (customer_id,))

    customer = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_customer.html",
        customer=customer
    )


# -------------------------------------------------
# UPDATE CUSTOMER
# -------------------------------------------------

@app.route("/update_customer/<int:customer_id>", methods=["POST"])
def update_customer(customer_id):

    if "username" not in session:
        return redirect("/")

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET
            name = %s,
            phone = %s,
            email = %s
        WHERE customer_id = %s
    """, (
        name,
        phone,
        email,
        customer_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/customers")


# -------------------------------------------------
# DELETE CUSTOMER
# -------------------------------------------------

@app.route("/delete_customer/<int:customer_id>")
def delete_customer(customer_id):

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM customers
            WHERE customer_id = %s
        """, (customer_id,))

        connection.commit()

    except mysql.connector.Error as error:

        connection.rollback()

        cursor.close()
        connection.close()

        return f"Cannot delete customer because this customer has a transaction.<br><br>{error}"

    cursor.close()
    connection.close()

    return redirect("/customers")


# -------------------------------------------------
# AGENTS
# -------------------------------------------------

@app.route("/agents")
def agents():

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY agent_id DESC
    """)

    agents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "agents.html",
        agents=agents
    )


# -------------------------------------------------
# ADD AGENT
# -------------------------------------------------

@app.route("/add_agent", methods=["POST"])
def add_agent():

    if "username" not in session:
        return redirect("/")

    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO agents
        (
            name,
            phone,
            email
        )
        VALUES (%s, %s, %s)
    """, (
        name,
        phone,
        email
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/agents")


# -------------------------------------------------
# TRANSACTIONS
# -------------------------------------------------

@app.route("/transactions")
def transactions():

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            t.transaction_id,
            c.name AS customer_name,
            p.property_type,
            p.location,
            a.name AS agent_name,
            t.amount,
            t.transaction_date
        FROM transactions t
        JOIN customers c
            ON t.customer_id = c.customer_id
        JOIN properties p
            ON t.property_id = p.property_id
        JOIN agents a
            ON t.agent_id = a.agent_id
        ORDER BY t.transaction_id DESC
    """)

    transactions = cursor.fetchall()

    # Customers
    cursor.execute("""
        SELECT *
        FROM customers
        ORDER BY name
    """)

    customers = cursor.fetchall()

    # Properties
    cursor.execute("""
        SELECT *
        FROM properties
        WHERE status != 'Sold'
        ORDER BY property_id DESC
    """)

    properties = cursor.fetchall()

    # Agents
    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY name
    """)

    agents = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "transactions.html",
        transactions=transactions,
        customers=customers,
        properties=properties,
        agents=agents
    )


# -------------------------------------------------
# ADD TRANSACTION
# -------------------------------------------------

@app.route("/add_transaction", methods=["POST"])
def add_transaction():

    if "username" not in session:
        return redirect("/")

    customer_id = request.form["customer_id"]
    property_id = request.form["property_id"]
    agent_id = request.form["agent_id"]
    amount = request.form["amount"]
    transaction_date = request.form["transaction_date"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        # Add transaction
        cursor.execute("""
            INSERT INTO transactions
            (
                customer_id,
                property_id,
                agent_id,
                amount,
                transaction_date
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            customer_id,
            property_id,
            agent_id,
            amount,
            transaction_date
        ))

        # Automatically mark property as Sold
        cursor.execute("""
            UPDATE properties
            SET status = 'Sold'
            WHERE property_id = %s
        """, (property_id,))

        connection.commit()

    except mysql.connector.Error as error:

        connection.rollback()

        cursor.close()
        connection.close()

        return f"Transaction could not be added.<br><br>{error}"

    cursor.close()
    connection.close()

    return redirect("/transactions")


# -------------------------------------------------
# REPORTS
# -------------------------------------------------

@app.route("/reports")
def reports():

    if "username" not in session:
        return redirect("/")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Total properties
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM properties
    """)

    total_properties = cursor.fetchone()["total"]

    # Total customers
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM customers
    """)

    total_customers = cursor.fetchone()["total"]

    # Total agents
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM agents
    """)

    total_agents = cursor.fetchone()["total"]

    # Total transactions
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM transactions
    """)

    total_transactions = cursor.fetchone()["total"]

    # Total sales
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM transactions
    """)

    total_sales = cursor.fetchone()["total"]

    # Property status report
    cursor.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM properties
        GROUP BY status
    """)

    property_status = cursor.fetchall()

    # Agent property report
    cursor.execute("""
        SELECT
            a.name AS agent_name,
            COUNT(p.property_id) AS property_count
        FROM agents a
        LEFT JOIN properties p
            ON a.agent_id = p.agent_id
        GROUP BY a.agent_id, a.name
        ORDER BY property_count DESC
    """)

    agent_report = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        total_properties=total_properties,
        total_customers=total_customers,
        total_agents=total_agents,
        total_transactions=total_transactions,
        total_sales=total_sales,
        property_status=property_status,
        agent_report=agent_report
    )


# -------------------------------------------------
# START APPLICATION
# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)