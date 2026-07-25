from flask import Flask,render_template,request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
app = Flask(__name__)
app.config['SECRET_KEY'] = "HarvestIQ@123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# ==========================
# User Model
# ==========================

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15))
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    farmer = db.relationship(
        "Farmer",
        back_populates="user",
        uselist=False
    )

    buyer = db.relationship(
        "Buyer",
        back_populates="user",
        uselist=False
    )

    logistics = db.relationship(
        "LogisticsProvider",
        back_populates="user",
        uselist=False
    )


# ==========================
# Farmer Model
# ==========================

class Farmer(db.Model):
    __tablename__ = "farmers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    land_size = db.Column(db.Float)
    farmer_type = db.Column(db.String(30))
    fpo_member = db.Column(db.Boolean)
    income_category = db.Column(db.String(30))

    user = db.relationship(
        "User",
        back_populates="farmer"
    )

    produce_batches = db.relationship(
        "ProduceBatch",
        back_populates="farmer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    subsidy_applications = db.relationship(
        "SubsidyApplication",
        back_populates="farmer",
        lazy=True
    )


# ==========================
# Buyer Model
# ==========================

class Buyer(db.Model):
    __tablename__ = "buyers"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    company_name = db.Column(db.String(100))
    buyer_type = db.Column(db.String(50))
    city = db.Column(db.String(50))

    user = db.relationship(
        "User",
        back_populates="buyer"
    )

    purchases = db.relationship(
        "Sale",
        back_populates="buyer",
        lazy=True
    )


# ==========================
# Logistics Provider Model
# ==========================

class LogisticsProvider(db.Model):
    __tablename__ = "logistics"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    company_name = db.Column(db.String(100))

    user = db.relationship(
        "User",
        back_populates="logistics"
    )

    deliveries = db.relationship(
        "Delivery",
        back_populates="logistics",
        lazy=True
    )


# ==========================
# Produce Batch Model
# ==========================

class ProduceBatch(db.Model):
    __tablename__ = "produce_batches"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    crop_name = db.Column(db.String(50))
    variety = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(20))
    harvest_date = db.Column(db.Date)
    farm_location = db.Column(db.String(200))

    status = db.Column(
        db.String(30),
        default="Registered"
    )

    farmer = db.relationship(
        "Farmer",
        back_populates="produce_batches"
    )

    quality = db.relationship(
        "QualityInspection",
        back_populates="batch",
        uselist=False,
        lazy=True
    )

    shelf_life = db.relationship(
        "ShelfLifePrediction",
        back_populates="batch",
        uselist=False,
        lazy=True
    )

    storage = db.relationship(
        "StorageRecord",
        back_populates="batch",
        lazy=True
    )

    deliveries = db.relationship(
        "Delivery",
        back_populates="batch",
        lazy=True
    )

    recommendation = db.relationship(
        "Recommendation",
        back_populates="batch",
        uselist=False,
        lazy=True
    )

    sale = db.relationship(
        "Sale",
        back_populates="batch",
        uselist=False,
        lazy=True
    )
# ==========================
# Quality Inspection Model
# ==========================

class QualityInspection(db.Model):
    __tablename__ = "quality_inspections"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False,
        unique=True
    )

    quality_grade = db.Column(db.String(20))
    quality_score = db.Column(db.Float)
    freshness = db.Column(db.String(30))
    damaged_percentage = db.Column(db.Float)
    inspection_date = db.Column(db.Date)

    batch = db.relationship(
        "ProduceBatch",
        back_populates="quality"
    )


# ==========================
# Shelf Life Prediction Model
# ==========================

class ShelfLifePrediction(db.Model):
    __tablename__ = "shelf_life"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False,
        unique=True
    )

    predicted_days = db.Column(db.Integer)
    confidence = db.Column(db.Float)
    spoilage_risk = db.Column(db.String(20))

    batch = db.relationship(
        "ProduceBatch",
        back_populates="shelf_life"
    )


# ==========================
# Storage Record Model
# ==========================

class StorageRecord(db.Model):
    __tablename__ = "storage_records"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False
    )

    storage_type = db.Column(db.String(30))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    storage_date = db.Column(db.Date)

    batch = db.relationship(
        "ProduceBatch",
        back_populates="storage"
    )


# ==========================
# Delivery Model
# ==========================

class Delivery(db.Model):
    __tablename__ = "deliveries"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False
    )

    logistics_id = db.Column(
        db.Integer,
        db.ForeignKey("logistics.id"),
        nullable=False
    )

    source = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    status = db.Column(db.String(30))
    eta = db.Column(db.DateTime)
    transport_temperature = db.Column(db.Float)

    batch = db.relationship(
        "ProduceBatch",
        back_populates="deliveries"
    )

    logistics = db.relationship(
        "LogisticsProvider",
        back_populates="deliveries"
    )


# ==========================
# Recommendation Model
# ==========================

class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False,
        unique=True
    )

    recommendation_type = db.Column(db.String(50))
    suggested_destination = db.Column(db.String(100))
    estimated_price = db.Column(db.Float)
    reason = db.Column(db.Text)

    batch = db.relationship(
        "ProduceBatch",
        back_populates="recommendation"
    )


# ==========================
# Sale Model
# ==========================

class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)

    batch_id = db.Column(
        db.Integer,
        db.ForeignKey("produce_batches.id"),
        nullable=False,
        unique=True
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyers.id"),
        nullable=False
    )

    sale_price = db.Column(db.Float)
    sale_date = db.Column(db.Date)
    quantity_sold = db.Column(db.Integer)

    batch = db.relationship(
        "ProduceBatch",
        back_populates="sale"
    )

    buyer = db.relationship(
        "Buyer",
        back_populates="purchases"
    )


# ==========================
# Subsidy Model
# ==========================

class Subsidy(db.Model):
    __tablename__ = "subsidies"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    state = db.Column(db.String(50))
    eligibility = db.Column(db.Text)
    benefits = db.Column(db.Text)
    last_date = db.Column(db.Date)
    required_documents = db.Column(db.Text)

    applications = db.relationship(
        "SubsidyApplication",
        back_populates="subsidy",
        lazy=True
    )


# ==========================
# Subsidy Application Model
# ==========================

class SubsidyApplication(db.Model):
    __tablename__ = "subsidy_applications"

    id = db.Column(db.Integer, primary_key=True)

    farmer_id = db.Column(
        db.Integer,
        db.ForeignKey("farmers.id"),
        nullable=False
    )

    subsidy_id = db.Column(
        db.Integer,
        db.ForeignKey("subsidies.id"),
        nullable=False
    )

    application_date = db.Column(db.Date)

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    farmer = db.relationship(
        "Farmer",
        back_populates="subsidy_applications"
    )

    subsidy = db.relationship(
        "Subsidy",
        back_populates="applications"
    )
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        role = request.form["role"]

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists!")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        # Create User
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            phone=phone,
            role=role
        )

        db.session.add(user)
        db.session.flush()   # Generates user.id before commit

        # Create Role Profile
        if role == "Farmer":

            farmer = Farmer(
                user_id=user.id,
                state=request.form["state"],
                district=request.form["district"],
                land_size=float(request.form["land_size"]),
                farmer_type=request.form["farmer_type"],
                fpo_member=True if request.form.get("fpo_member") else False,
                income_category=request.form["income_category"]
            )

            db.session.add(farmer)

        elif role == "Buyer":

            buyer = Buyer(
                user_id=user.id,
                company_name=request.form["company_name"],
                buyer_type=request.form["buyer_type"],
                city=request.form["city"]
            )

            db.session.add(buyer)

        elif role == "Logistics":

            logistics = LogisticsProvider(
                user_id=user.id,
                company_name=request.form["company_name"]
            )

            db.session.add(logistics)

        # Save to database
        db.session.commit()

        flash("Registration Successful! Please Login.")

        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):

            session["user_id"] = user.id
            session["role"] = user.role
            session["name"] = user.full_name

            if user.role == "Farmer":
                return "Farmer Dashboard"

            elif user.role == "Buyer":
                return "Buyer Dashboard"

            elif user.role == "Logistics":
                return "logistics_dashboard"

        flash("Invalid Email or Password")

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))
# ==========================
# Run Application
# ==========================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)