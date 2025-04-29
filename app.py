from flask import Flask, render_template, redirect, url_for, request, flash
from forms import RegisterForm, LoginForm, SOSForm, ReportForm
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Import from database.py
from database import db, login_manager, migrate
# Import models
from models import User, SOSContact, CrimeReport  

# Email constants - replace with actual values
EMAIL_ADDRESS = "your_email@gmail.com"  # Replace with your actual email
EMAIL_PASSWORD = "your_password"        # Replace with your actual password

# App factory pattern
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Ensure that tables are created
    with app.app_context():
        db.create_all()

    # Routes
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                password=hashed_pw,
                age=form.age.data,
                gender=form.gender.data,
                phone=form.phone.data
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        return render_template('auth/register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            flash('Invalid credentials', 'danger')
        return render_template('auth/login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/map')
    def map_page():
        from load_crime_data import load_crime_data
        crimes = load_crime_data()
        return render_template('map.html', crimes=crimes)

    @app.route('/sos', methods=['GET', 'POST'])
    @login_required
    def sos():
        form = SOSForm()
        if form.validate_on_submit():
            new_contact = SOSContact(phone=form.phone.data, user_id=current_user.id)
            db.session.add(new_contact)
            db.session.commit()
            flash('Contact added.', 'success')
        contacts = SOSContact.query.filter_by(user_id=current_user.id).all()
        return render_template('sos.html', contacts=contacts, form=form)

    @app.route('/send_sos')
    @login_required
    def send_sos():
        contacts = SOSContact.query.filter_by(user_id=current_user.id).all()
        for contact in contacts:
            send_email(contact.phone)
        flash('SOS alerts sent!', 'success')
        return redirect(url_for('sos'))

    def send_email(contact_phone):
        subject = "SOS Alert: Emergency Help Needed!"
        body = "Your family member is in danger. Please reach out immediately."

        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = contact_phone
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
            print(f"Email sent to {contact_phone}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

    @app.route('/report', methods=['GET', 'POST'])
    @login_required
    def report():
        form = ReportForm()
        if form.validate_on_submit():
            new_report = CrimeReport(content=form.content.data, user_id=current_user.id)
            db.session.add(new_report)
            db.session.commit()
            flash('Report submitted.', 'success')
            return redirect(url_for('news'))
        return render_template('report.html', form=form)

    @app.route('/news')
    def news():
        reports = CrimeReport.query.all()
        return render_template('news.html', reports=reports)

    return app

# Run the application
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
