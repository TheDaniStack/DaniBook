from app import danibook
from flask import render_template, json, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

#home routes
@danibook.route("/")
def home():
    return render_template("home.html")


@danibook.route("/services")
def services():
    with open("data/services.json", "r") as file:
        services_data = json.load(file)

    return render_template("services.html", services=services_data)


@danibook.template_filter()
def format_price(price):
    return f"{price:,}"

#booking routes
@danibook.route("/booking", methods=["GET", "POST"])
def booking():

    if "user_email" not in session:
        return redirect(url_for("login"))
  
    selected_service = request.args.get("service")

    if request.method == "POST":
        date = request.form.get("date")
        time = request.form.get("time")
        phone_number = request.form.get("phone-number")
        user_text = request.form.get("user-text")
        service = request.form.get("service")

        print(repr(service))

        if not date or not time or not phone_number:
            return render_template(
                "booking.html",
                error="Date, Time and phone number are required",
                selected_service=service
            )

        booking_date = datetime.strptime(
            date,
            "%Y-%m-%d"
        ).date()

        current_date = datetime.today().date()

        if booking_date < current_date:
            return render_template(
                "booking.html",
                error="Booking date can't be in the past",
                selected_service=service
            )

        booking_datetime = datetime.strptime(
            f"{date} {time}",
            "%Y-%m-%d %H:%M"
        )

        current_datetime = datetime.today()

        time_until_booking = booking_datetime - current_datetime

        minimum_advance_time = timedelta(hours=2)

        if time_until_booking < minimum_advance_time:
            return render_template(
                "booking.html",
                error="Bookings must be made at least 2 hours in advance",
                selected_service=service
            )

        booking_week = booking_date.weekday()

        if booking_week == 6:
            return render_template(
                "booking.html",
                error="Bookings can't be on Sundays",
                selected_service=service
            )

        with open("data/services.json", "r") as file:
            existing_services = json.load(file)

        selected_service_data = None

        for existing_service in existing_services:
            if existing_service["name"] == service:
                selected_service_data = existing_service
                break

        if selected_service_data is None:
            return render_template(
                "booking.html",
                selected_service=service,
                error="Invalid service selected"
            )

        return render_template(
            "booking.html",
            selected_service=service
        )

    return render_template(
        "booking.html",
        selected_service=selected_service
    )

  #register route
@danibook.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        full_name = request.form.get("user-name", "")
        email = request.form.get("user-email", "")
        password = request.form.get("user-password", "")
        confirm_password = request.form.get("confirm-password", "")

        # Required fields
        if not full_name or not email or not password or not confirm_password:
            return render_template(
                "register.html",
                error="All fields are required"
            )

        # Password length
        if len(password) < 8:
            return render_template(
                "register.html",
                error="Length of password must be 8 characters or above"
            )

        # Password confirmation
        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        with open("data/users.json", "r") as file:
            users = json.load(file)

        # Check for existing email
        for user in users:
            if user["email"] == email:
                return render_template(
                    "register.html",
                    error="An account with this email already exists"
                )

        # Hash password
        hashed_password = generate_password_hash(password)

        # New user
        new_user = {
            "name": full_name,
            "email": email,
            "password": hashed_password
        }

        users.append(new_user)

        # Save new user
        with open("data/users.json", "w") as file:
            json.dump(users, file, indent=4)

        return redirect(url_for("login"))

    return render_template("register.html")

#login routes
@danibook.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        login_email = request.form.get("login-email", "")
        login_password = request.form.get("login-password", "")

        with open("data/users.json", "r") as file:
            stored_users = json.load(file)

        for stored_user in stored_users:

            if stored_user["email"] == login_email:

                if check_password_hash(
                    stored_user["password"],
                    login_password
                ):
                    session["user_email"] = stored_user["email"]
                    return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


@danibook.route("/my-bookings")
def my_bookings():
    if "user_email" not in session:
        return redirect(url_for("login"))

    user_email = session["user_email"]

    with open("data/users.json", "r") as file:
        users = json.load(file)

    for user in users:
        if user["email"] == user_email:
            logged_in_user = user
            break

    return render_template(
        "my-bookings.html",
        logged_in_user=logged_in_user
    )