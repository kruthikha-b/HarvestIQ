import os
from werkzeug.utils import secure_filename
from flask import Flask,render_template,request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
app = Flask(__name__)
app.config['SECRET_KEY'] = "HarvestIQ@123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "connect_args": {
        "timeout": 30
    }
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"
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
    image = db.Column(db.String(200))

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
            flash("Email already exists!", "danger")
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

        flash("Registration Successful! Please Login.", "success")

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
            flash("Login successful! Welcome to HarvestIQ.", "success")
            if user.role == "Farmer":
                return redirect(url_for("farmer_dashboard"))

            elif user.role == "Buyer":
                return redirect(url_for("buyer_dashboard"))

            elif user.role == "Logistics":
                return "logistics_dashboard"

        flash("Invalid Email or Password","danger")

    return render_template("login.html")
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully.", "success")

    return redirect(url_for("home"))
@app.route("/farmer_dashboard")
def farmer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    farmer = Farmer.query.filter_by(user_id=user.id).first()

    total_batches = ProduceBatch.query.filter_by(farmer_id=farmer.id).count()

    recent_batches = ProduceBatch.query.filter_by(
        farmer_id=farmer.id
    ).order_by(
        ProduceBatch.harvest_date.desc()
    ).limit(5).all()

    return render_template(
        "farmer_dashboard.html",
        user=user,
        farmer=farmer,
        total_batches=total_batches,
        recent_batches=recent_batches
    )
@app.route("/profile")
def profile():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    farmer = Farmer.query.filter_by(user_id=user.id).first()

    return render_template(
        "profile.html",
        user=user,
        farmer=farmer
    )
@app.route("/register_produce", methods=["GET", "POST"])
def register_produce():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    farmer = Farmer.query.filter_by(user_id=user.id).first()

    if request.method == "POST":

        batch = ProduceBatch(

            farmer_id=farmer.id,

            crop_name=request.form["crop_name"],

            variety=request.form["variety"],

            quantity=int(request.form["quantity"]),

            unit=request.form["unit"],

            harvest_date=datetime.strptime(
                request.form["harvest_date"],
                "%Y-%m-%d"
            ).date(),

            farm_location=request.form["farm_location"],

            status="Registered"

        )

        db.session.add(batch)
        db.session.commit()

        flash("Produce Registered Successfully!", "success")

        return redirect(url_for("farmer_dashboard"))

    return render_template("register_produce.html")
@app.route("/my_produce")
def my_produce():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    farmer = Farmer.query.filter_by(user_id=user.id).first()

    batches = ProduceBatch.query.filter_by(
        farmer_id=farmer.id
    ).order_by(
        ProduceBatch.harvest_date.desc()
    ).all()

    return render_template(
        "my_produce.html",
        batches=batches
    )
@app.route("/delete_produce/<int:batch_id>")
def delete_produce(batch_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    db.session.delete(batch)
    db.session.commit()

    flash("Produce deleted successfully!", "success")

    return redirect(url_for("my_produce"))
@app.route("/edit_produce/<int:batch_id>", methods=["GET", "POST"])
def edit_produce(batch_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    if request.method == "POST":

        batch.crop_name = request.form["crop_name"]
        batch.variety = request.form["variety"]
        batch.quantity = int(request.form["quantity"])
        batch.unit = request.form["unit"]
        batch.harvest_date = datetime.strptime(
            request.form["harvest_date"],
            "%Y-%m-%d"
        ).date()
        batch.farm_location = request.form["farm_location"]

        db.session.commit()

        flash("Produce updated successfully!", "success")

        return redirect(url_for("my_produce"))

    return render_template(
        "edit_produce.html",
        batch=batch
    )
@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    farmer = Farmer.query.filter_by(user_id=user.id).first()

    if request.method == "POST":

        # User details
        user.full_name = request.form["full_name"]
        user.phone = request.form["phone"]

        # Farmer details
        farmer.state = request.form["state"]
        farmer.district = request.form["district"]
        farmer.land_size = float(request.form["land_size"])
        farmer.farmer_type = request.form["farmer_type"]
        farmer.income_category = request.form["income_category"]

        farmer.fpo_member = True if request.form.get("fpo_member") else False

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        user=user,
        farmer=farmer
    )
@app.route("/quality_inspection/<int:batch_id>", methods=["GET", "POST"])
def quality_inspection(batch_id):

    batch = ProduceBatch.query.get_or_404(batch_id)

    if request.method == "POST":

        image = request.files["image"]

        filename = secure_filename(image.filename)

        image.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        inspection = QualityInspection.query.filter_by(
            batch_id=batch.id
        ).first()

        if inspection is None:

            inspection = QualityInspection(
                batch_id=batch.id
            )

            db.session.add(inspection)

        inspection.image = filename

        # Dummy AI Result
        inspection.quality_grade = "A"
        inspection.quality_score = 95
        inspection.freshness = "Fresh"
        inspection.damaged_percentage = 3
        inspection.inspection_date = datetime.today()

        db.session.commit()

        flash("Quality Inspection Completed!", "success")

        return redirect(url_for("inspection_result", batch_id=batch.id))

    return render_template(
        "quality_inspection.html",
        batch=batch
    )
@app.route("/inspection_result/<int:batch_id>")
def inspection_result(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    inspection = QualityInspection.query.filter_by(
        batch_id=batch.id
    ).first()

    return render_template(
        "inspection_result.html",
        batch=batch,
        inspection=inspection
    )
@app.route("/shelf_life_prediction/<int:batch_id>")
def shelf_life_prediction(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    prediction = ShelfLifePrediction.query.filter_by(
        batch_id=batch.id
    ).first()

    if prediction is None:

        prediction = ShelfLifePrediction(
            batch_id=batch.id,
            predicted_days=8,
            confidence=96.5,
            spoilage_risk="Low"
        )

        db.session.add(prediction)
        db.session.commit()

    return render_template(
        "shelf_life.html",
        batch=batch,
        prediction=prediction
    )
@app.route("/delivery_tracking/<int:batch_id>")
def delivery_tracking(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    delivery = Delivery.query.filter_by(batch_id=batch.id).first()

    if delivery is None:

        logistics = LogisticsProvider.query.first()

        if logistics is None:
            flash("Please register a Logistics Provider first.", "warning")
            return redirect(url_for("register"))

        delivery = Delivery(
            batch_id=batch.id,
            logistics_id=logistics.id,
            source=batch.farm_location,
            destination="Hyderabad Fruit Market",
            status="Preparing",
            eta=datetime.now(),
            transport_temperature=6
        )

        db.session.add(delivery)
        db.session.commit()

    return render_template(
        "delivery_tracking.html",
        batch=batch,
        delivery=delivery
    )
@app.route("/mark_delivered/<int:delivery_id>")
def mark_delivered(delivery_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    delivery = Delivery.query.get_or_404(delivery_id)

    delivery.status = "Delivered"

    db.session.commit()

    flash("Delivery marked as completed!", "success")

    return redirect(
        url_for(
            "delivery_tracking",
            batch_id=delivery.batch_id
        )
    )
@app.route("/buyer_recommendation/<int:batch_id>")
def buyer_recommendation(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    recommendation = Recommendation.query.filter_by(
        batch_id=batch.id
    ).first()

    if recommendation is None:

        recommendation = Recommendation(
            batch_id=batch.id,
            recommendation_type="Wholesale Market",
            suggested_destination="Hyderabad Fruit Market",
            estimated_price=6500,
            reason="High quality produce with low spoilage risk. Suitable for wholesale buyers."
        )

        db.session.add(recommendation)
        db.session.commit()

    return render_template(
        "buyer_recommendation.html",
        batch=batch,
        recommendation=recommendation
    )
@app.route("/confirm_sale/<int:batch_id>", methods=["GET", "POST"])
def confirm_sale(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    recommendation = Recommendation.query.filter_by(
        batch_id=batch.id
    ).first()

    buyers = Buyer.query.all()

    if request.method == "POST":

        buyer_id = request.form["buyer_id"]

        sale = Sale.query.filter_by(batch_id=batch.id).first()

        if sale is None:

            sale = Sale(
                batch_id=batch.id,
                buyer_id=buyer_id,
                sale_price=recommendation.estimated_price,
                quantity_sold=batch.quantity,
                sale_date=datetime.today()
            )

            db.session.add(sale)

        batch.status = "Sold"

        db.session.commit()

        flash("Sale completed successfully!", "success")

        return redirect(url_for("sale_receipt", sale_id=sale.id))

    return render_template(
        "confirm_sale.html",
        batch=batch,
        buyers=buyers,
        recommendation=recommendation
    )
@app.route("/sale_receipt/<int:sale_id>")
def sale_receipt(sale_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    sale = Sale.query.get_or_404(sale_id)

    return render_template(
        "sale_receipt.html",
        sale=sale
    )
@app.route("/sales_history")
def sales_history():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    farmer = Farmer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    sales = Sale.query.join(ProduceBatch).filter(
        ProduceBatch.farmer_id == farmer.id
    ).order_by(Sale.sale_date.desc()).all()

    total_sales = sum(sale.sale_price for sale in sales)

    return render_template(
        "sales_history.html",
        sales=sales,
        total_sales=total_sales
    )
@app.route("/apply_subsidy/<int:subsidy_id>")
def apply_subsidy(subsidy_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    farmer = Farmer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    subsidy = Subsidy.query.get_or_404(subsidy_id)

    # Check if already applied
    existing = SubsidyApplication.query.filter_by(
        farmer_id=farmer.id,
        subsidy_id=subsidy.id
    ).first()

    if existing:
        flash("You have already applied for this subsidy.", "warning")
        return redirect(url_for("view_subsidies"))

    application = SubsidyApplication(
        farmer_id=farmer.id,
        subsidy_id=subsidy.id,
        application_date=date.today(),
        status="Pending"
    )

    db.session.add(application)
    db.session.commit()

    flash("Subsidy application submitted successfully!", "success")

    return redirect(url_for("view_subsidies"))
@app.route("/view_subsidies")
def view_subsidies():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    farmer = Farmer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    applications = SubsidyApplication.query.filter_by(
        farmer_id=farmer.id
    ).all()

    return render_template(
        "view_subsidies.html",
        applications=applications
    )
@app.route("/buyer_dashboard")
def buyer_dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    buyer = Buyer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    available_batches = ProduceBatch.query.filter(
        ProduceBatch.status != "Sold"
    ).all()

    total_available = len(available_batches)

    return render_template(
        "buyer_dashboard.html",
        buyer=buyer,
        total_available=total_available,
        available_batches=available_batches[:5]
    )
@app.route("/available_produce")
def available_produce():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    buyer = Buyer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    search = request.args.get("search", "")

    if search:

        batches = ProduceBatch.query.filter(
            ProduceBatch.status != "Sold",
            ProduceBatch.crop_name.ilike(f"%{search}%")
        ).all()

    else:

        batches = ProduceBatch.query.filter(
            ProduceBatch.status != "Sold"
        ).all()

    return render_template(
        "available_produce.html",
        buyer=buyer,
        batches=batches,
        search=search
    )
@app.route("/view_produce/<int:batch_id>")
def view_produce(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    batch = ProduceBatch.query.get_or_404(batch_id)

    quality = QualityInspection.query.filter_by(
        batch_id=batch.id
    ).first()

    shelf = ShelfLifePrediction.query.filter_by(
        batch_id=batch.id
    ).first()

    recommendation = Recommendation.query.filter_by(
        batch_id=batch.id
    ).first()

    return render_template(
        "view_produce.html",
        batch=batch,
        quality=quality,
        shelf=shelf,
        recommendation=recommendation
    )
@app.route("/purchase_history")
def purchase_history():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    buyer = Buyer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    purchases = Sale.query.filter_by(
        buyer_id=buyer.id
    ).order_by(Sale.sale_date.desc()).all()

    return render_template(
        "purchase_history.html",
        purchases=purchases
    )
@app.route("/buy_produce/<int:batch_id>")
def buy_produce(batch_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    buyer = Buyer.query.filter_by(
        user_id=session["user_id"]
    ).first_or_404()

    batch = ProduceBatch.query.get_or_404(batch_id)

    if batch.status == "Sold":
        flash("This produce has already been sold.", "danger")
        return redirect(url_for("available_produce"))

    recommendation = Recommendation.query.filter_by(
        batch_id=batch.id
    ).first()

    if recommendation:
        price = recommendation.estimated_price
    else:
        price = 5000

    sale = Sale(
        batch_id=batch.id,
        buyer_id=buyer.id,
        sale_price=price,
        quantity_sold=batch.quantity,
        sale_date=date.today()
    )

    batch.status = "Sold"

    db.session.add(sale)
    db.session.commit()

    flash("Purchase completed successfully!", "success")

    return redirect(url_for("sale_receipt", sale_id=sale.id))
@app.route("/buyer_receipt/<int:sale_id>")
def buyer_receipt(sale_id):

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    sale = Sale.query.get_or_404(sale_id)

    buyer = Buyer.query.filter_by(user_id=session["user_id"]).first_or_404()

    if sale.buyer_id != buyer.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for("purchase_history"))

    return render_template(
        "buyer_receipt.html",
        sale=sale
    )
@app.route("/buyer_profile", methods=["GET", "POST"])
def buyer_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    buyer = Buyer.query.filter_by(user_id=user.id).first()

    if request.method == "POST":

        user.full_name = request.form["full_name"]
        user.email = request.form["email"]
        user.phone = request.form["phone"]

        buyer.company_name = request.form["company_name"]
        buyer.buyer_type = request.form["buyer_type"]
        buyer.city = request.form["city"]

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("buyer_profile"))

    return render_template(
        "buyer_profile.html",
        user=user,
        buyer=buyer
    )
@app.route("/update_buyer_profile", methods=["POST"])
def update_buyer_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    buyer = Buyer.query.filter_by(user_id=user.id).first()

    user.full_name = request.form["full_name"]
    user.email = request.form["email"]
    user.phone = request.form["phone"]

    buyer.company_name = request.form["company_name"]
    buyer.buyer_type = request.form["buyer_type"]
    buyer.city = request.form["city"]

    db.session.commit()

    session["name"] = user.full_name

    flash("Buyer profile updated successfully!", "success")

    return redirect(url_for("buyer_profile"))
# ==========================
# Run Application
# ==========================
if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        if Subsidy.query.count() == 0:

            db.session.add(Subsidy(
                name="PM-KISAN",
                state="All India",
                eligibility="Small and marginal farmers",
                benefits="₹6000 per year financial assistance",
                last_date=date(2026, 12, 31),
                required_documents="Aadhaar Card, Bank Passbook, Land Records"
            ))

            db.session.add(Subsidy(
                name="Cold Storage Subsidy",
                state="Telangana",
                eligibility="Registered farmers with produce storage needs",
                benefits="Up to 50% subsidy on cold storage expenses",
                last_date=date(2026, 11, 30),
                required_documents="Farmer ID, Land Records, Storage Proposal"
            ))

            db.session.add(Subsidy(
                name="Organic Farming Scheme",
                state="All India",
                eligibility="Farmers practising organic farming",
                benefits="Financial assistance for organic cultivation",
                last_date=date(2026, 10, 31),
                required_documents="Organic Certification, Aadhaar Card"
            ))

            db.session.commit()

            print("Sample subsidies inserted successfully!")

    app.run(debug=True)