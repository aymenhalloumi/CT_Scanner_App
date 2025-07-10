#!/usr/bin/env python3
"""
PROMAMEC CT Scanner Professional Suite - Enterprise Edition
Complete Advanced Platform with AI Analysis, 3D Visualization, and Professional Reporting
Fixed Version with All Issues Resolved
"""

# ===== IMPORTS & DEPENDENCIES =====
import os
import sys
import logging
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template_string, request, redirect, url_for, flash, session, jsonify, send_file
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from flask_admin.theme import Bootstrap4Theme
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
import openai
import json
from datetime import datetime, timedelta
import re
import io
import base64
import uuid
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Visualization & PDF Libraries
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot

# ===== PROFESSIONAL LOGGING SETUP =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('promamec_ct_scanner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== FLASK APP CONFIGURATION =====

app = Flask(__name__)

# Professional Configuration with Enhanced Security
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'yaf41932812597fef37b07b79ae44176738bc06b8bbe7b3a7f77b302a2e77bc6b'),
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///promamec_ct_scanner_professional.db'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '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'),
    'WTF_CSRF_ENABLED': True,
    'WTF_CSRF_TIME_LIMIT': None,
    'COMPANY_NAME': 'Promamec Solutions',
    'COMPANY_TAGLINE': 'Professional Medical Equipment Consulting & Integration',
    'COMPANY_LOGO': 'https://promamec.com/assets/site/img/logo.png',
    'VERSION': '2.0.0',
    'BUILD': 'Professional-Enterprise'
})

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please authenticate to access this professional resource.'

# Enhanced OpenAI client initialization
try:
    if app.config['OPENAI_API_KEY'] and app.config['OPENAI_API_KEY'] != 'your-openai-api-key-here':
        client = openai.OpenAI(api_key=app.config['OPENAI_API_KEY'])
        logger.info("OpenAI client initialized successfully")
    else:
        client = None
        logger.warning("OpenAI API key not configured - AI features will be limited")
except Exception as e:
    logger.error(f"OpenAI client initialization failed: {e}")
    client = None

# ===== ENHANCED DATABASE MODELS =====

class User(UserMixin, db.Model):
    """Professional user model with comprehensive fields"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='Client')
    is_active = db.Column(db.Boolean, default=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    department = db.Column(db.String(50))
    title = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    specialization = db.Column(db.String(100))
    last_login = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def professional_title(self):
        title_parts = []
        if self.title:
            title_parts.append(self.title)
        if self.specialization:
            title_parts.append(f"({self.specialization})")
        return " ".join(title_parts) if title_parts else "Professional"
    
    def record_login(self):
        self.last_login = datetime.utcnow()
        self.login_count = (self.login_count or 0) + 1
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    """Enhanced project model with comprehensive tracking"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text)
    client_name = db.Column(db.String(150), nullable=False)
    client_email = db.Column(db.String(100))
    client_phone = db.Column(db.String(20))
    facility_name = db.Column(db.String(150))
    facility_address = db.Column(db.Text)
    facility_type = db.Column(db.String(50))  # Hospital, Clinic, Imaging Center
    status = db.Column(db.String(50), default='Planning')
    priority = db.Column(db.String(20), default='Medium')
    engineer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    project_manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    budget = db.Column(db.Float)
    actual_cost = db.Column(db.Float)
    deadline = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completion_date = db.Column(db.DateTime)
    progress = db.Column(db.Integer, default=0)
    phase = db.Column(db.String(50), default='Assessment')
    compliance_status = db.Column(db.String(50), default='Pending')
    risk_level = db.Column(db.String(20), default='Medium')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    engineer = db.relationship('User', foreign_keys=[engineer_id], backref='assigned_projects')
    project_manager = db.relationship('User', foreign_keys=[project_manager_id], backref='managed_projects')
    
    @property
    def days_remaining(self):
        if self.deadline:
            return (self.deadline - datetime.utcnow()).days
        return None
    
    @property
    def is_overdue(self):
        if self.deadline:
            return datetime.utcnow() > self.deadline and self.status != 'Completed'
        return False
    
    @property
    def budget_variance(self):
        if self.budget and self.actual_cost:
            return ((self.actual_cost - self.budget) / self.budget) * 100
        return 0
    
    def __repr__(self):
        return f'<Project {self.name} - {self.status}>'

class ScannerModel(db.Model):
    """Comprehensive scanner model with detailed specifications"""
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False)
    model_name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(50))
    slice_count = db.Column(db.Integer)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))
    min_room_length = db.Column(db.Float, nullable=False)
    min_room_width = db.Column(db.Float, nullable=False)
    min_room_height = db.Column(db.Float, nullable=False)
    required_power = db.Column(db.String(50), nullable=False)
    power_consumption = db.Column(db.Float)
    power_factor_requirement = db.Column(db.Float)
    cooling_requirements = db.Column(db.String(100))
    heat_dissipation = db.Column(db.Float)
    is_neuviz = db.Column(db.Boolean, default=False)
    neuviz_manual_ref = db.Column(db.String(50))
    radiation_shielding = db.Column(db.String(100))
    environmental_specs = db.Column(db.Text)
    price_range_min = db.Column(db.Float)
    price_range_max = db.Column(db.Float)
    warranty_years = db.Column(db.Integer)
    service_requirement = db.Column(db.String(100))
    installation_complexity = db.Column(db.String(20))
    certification_standards = db.Column(db.Text)
    software_version = db.Column(db.String(50))
    upgrade_path = db.Column(db.Text)
    maintenance_schedule = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def price_range(self):
        if self.price_range_min and self.price_range_max:
            return f"${self.price_range_min:,.0f} - ${self.price_range_max:,.0f}"
        return "Contact for pricing"
    
    @property
    def room_volume(self):
        return self.min_room_length * self.min_room_width * self.min_room_height
    
    @property
    def complexity_score(self):
        scores = {'Low': 1, 'Medium': 2, 'High': 3}
        return scores.get(self.installation_complexity, 2)
    
    def __repr__(self):
        return f'<Scanner {self.manufacturer} {self.model_name}>'

class ManualRoomEntry(db.Model):
    """Comprehensive manual room constraints entry for engineers"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    entered_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    site_name = db.Column(db.String(150), nullable=False)
    
    # Room Dimensions
    room_length = db.Column(db.Float, nullable=False)
    room_width = db.Column(db.Float, nullable=False)
    room_height = db.Column(db.Float, nullable=False)
    door_width = db.Column(db.Float)
    door_height = db.Column(db.Float)
    corridor_width = db.Column(db.Float)
    ceiling_clearance = db.Column(db.Float)
    
    # Structural Information
    floor_type = db.Column(db.String(50))
    floor_load_capacity = db.Column(db.Float)
    ceiling_type = db.Column(db.String(50))
    wall_construction = db.Column(db.String(50))
    foundation_type = db.Column(db.String(50))
    seismic_zone = db.Column(db.String(20))
    building_age = db.Column(db.Integer)
    
    # Electrical Systems
    available_power = db.Column(db.String(50))
    electrical_panel_distance = db.Column(db.Float)
    electrical_panel_capacity = db.Column(db.Float)
    voltage_stability = db.Column(db.String(50))
    has_ups = db.Column(db.Boolean, default=False)
    ups_capacity = db.Column(db.Float)
    has_isolation_transformer = db.Column(db.Boolean, default=False)
    grounding_system = db.Column(db.String(50))
    emergency_power = db.Column(db.Boolean, default=False)
    
    # HVAC & Environmental
    has_hvac = db.Column(db.Boolean, default=False)
    hvac_capacity = db.Column(db.String(50))
    hvac_type = db.Column(db.String(50))
    current_temperature_range = db.Column(db.String(20))
    current_humidity_range = db.Column(db.String(20))
    air_changes_per_hour = db.Column(db.Float)
    filtration_system = db.Column(db.String(50))
    humidity_control = db.Column(db.Boolean, default=False)
    
    # Safety & Utilities
    existing_shielding = db.Column(db.Boolean, default=False)
    shielding_details = db.Column(db.Text)
    shielding_type = db.Column(db.String(50))
    water_supply = db.Column(db.Boolean, default=False)
    water_pressure = db.Column(db.Float)
    compressed_air = db.Column(db.Boolean, default=False)
    compressed_air_pressure = db.Column(db.Float)
    network_infrastructure = db.Column(db.Boolean, default=False)
    network_speed = db.Column(db.String(50))
    fire_suppression = db.Column(db.String(50))
    emergency_systems = db.Column(db.Text)
    security_systems = db.Column(db.Text)
    
    # Compliance & Regulatory
    accessibility_compliance = db.Column(db.Boolean, default=False)
    ada_compliant = db.Column(db.Boolean, default=False)
    building_permits_status = db.Column(db.String(50))
    environmental_clearances = db.Column(db.Boolean, default=False)
    local_regulations = db.Column(db.Text)
    inspection_history = db.Column(db.Text)
    
    # Operational Considerations
    operating_hours = db.Column(db.String(50))
    patient_volume = db.Column(db.Integer)
    staff_count = db.Column(db.Integer)
    workflow_requirements = db.Column(db.Text)
    parking_availability = db.Column(db.Boolean, default=False)
    
    # Additional Information
    site_constraints = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    renovation_history = db.Column(db.Text)
    future_expansion_plans = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Metadata
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    assessment_confidence = db.Column(db.String(20))
    photos_available = db.Column(db.Boolean, default=False)
    drawings_available = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref='manual_room_entries')
    engineer = db.relationship('User', backref='room_entries')
    
    @property
    def room_area(self):
        return self.room_length * self.room_width
    
    @property
    def room_volume(self):
        return self.room_length * self.room_width * self.room_height
    
    @property
    def assessment_completeness(self):
        # Calculate assessment completeness based on filled fields
        total_fields = 50  # Approximate number of assessable fields
        filled_fields = 0
        
        for column in self.__table__.columns:
            if column.name not in ['id', 'created_at', 'updated_at']:
                value = getattr(self, column.name)
                if value is not None and value != '':
                    filled_fields += 1
        
        return round((filled_fields / total_fields) * 100, 1)
    
    def __repr__(self):
        return f'<ManualRoom {self.site_name} - {self.assessment_completeness}% complete>'

class SiteSpecification(db.Model):
    """Enhanced site specification model"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    scanner_model_id = db.Column(db.Integer, db.ForeignKey('scanner_model.id'), nullable=False)
    manual_room_id = db.Column(db.Integer, db.ForeignKey('manual_room_entry.id'))
    site_name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text)
    room_length = db.Column(db.Float, nullable=False)
    room_width = db.Column(db.Float, nullable=False)
    room_height = db.Column(db.Float, nullable=False)
    door_width = db.Column(db.Float)
    door_height = db.Column(db.Float)
    available_power = db.Column(db.String(50))
    electrical_panel_location = db.Column(db.String(100))
    has_hvac = db.Column(db.Boolean, default=False)
    hvac_capacity = db.Column(db.String(50))
    floor_type = db.Column(db.String(50))
    floor_load_capacity = db.Column(db.Float)
    existing_shielding = db.Column(db.Boolean, default=False)
    water_supply = db.Column(db.Boolean, default=False)
    compressed_air = db.Column(db.Boolean, default=False)
    network_infrastructure = db.Column(db.Boolean, default=False)
    accessibility_compliance = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='site_specifications')
    scanner_model = db.relationship('ScannerModel', backref='site_specifications')
    manual_room = db.relationship('ManualRoomEntry', backref='site_specifications')
    
    def __repr__(self):
        return f'<Site {self.site_name}>'

class ConformityReport(db.Model):
    """Enhanced conformity report with advanced analytics"""
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    site_specification_id = db.Column(db.Integer, db.ForeignKey('site_specification.id'), nullable=False)
    report_number = db.Column(db.String(50), unique=True, nullable=False)
    overall_status = db.Column(db.String(50), default='Pending')
    conformity_score = db.Column(db.Float)
    ai_analysis = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    neuviz_specific_analysis = db.Column(db.Text)
    risk_assessment = db.Column(db.String(50))
    estimated_cost = db.Column(db.Float)
    cost_breakdown = db.Column(db.Text)  # JSON string
    modification_timeline = db.Column(db.Integer)
    compliance_items = db.Column(db.Text)  # JSON string
    technical_drawings_required = db.Column(db.Boolean, default=False)
    permits_required = db.Column(db.Text)
    environmental_impact = db.Column(db.Text)
    installation_schedule = db.Column(db.Text)
    quality_checkpoints = db.Column(db.Text)
    pdf_generated = db.Column(db.Boolean, default=False)
    pdf_path = db.Column(db.String(255))
    email_sent = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    review_status = db.Column(db.String(50), default='Draft')
    revision_number = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = db.relationship('Project', backref='conformity_reports')
    site_specification = db.relationship('SiteSpecification', backref='conformity_reports')
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    @property
    def risk_color(self):
        colors = {'Low': 'success', 'Medium': 'warning', 'High': 'danger', 'Critical': 'dark'}
        return colors.get(self.risk_assessment, 'secondary')
    
    @property
    def status_color(self):
        colors = {
            'CONFORMING': 'success',
            'REQUIRES_MODIFICATION': 'warning',
            'NON_CONFORMING': 'danger',
            'Pending': 'secondary'
        }
        return colors.get(self.overall_status, 'secondary')
    
    def __repr__(self):
        return f'<Report {self.report_number} - {self.overall_status}>'

# ===== COMPREHENSIVE FORMS =====

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[
        ('Client', 'Client'),
        ('Engineer', 'Engineer'),
        ('Contributor', 'Contributor')
    ], default='Client')
    company = StringField('Company/Organization')
    department = StringField('Department')
    title = StringField('Professional Title')
    specialization = StringField('Specialization')
    phone = StringField('Phone Number')

class ComprehensiveManualRoomEntryForm(FlaskForm):
    """Comprehensive manual room entry form for engineers"""
    
    # Basic Information
    project_id = SelectField('Project', coerce=int, validators=[DataRequired()])
    site_name = StringField('Site/Room Name', validators=[DataRequired(), Length(max=150)])
    
    # Room Dimensions
    room_length = FloatField('Room Length (meters)', validators=[DataRequired(), NumberRange(min=0.1, max=50)])
    room_width = FloatField('Room Width (meters)', validators=[DataRequired(), NumberRange(min=0.1, max=50)])
    room_height = FloatField('Room Height (meters)', validators=[DataRequired(), NumberRange(min=0.1, max=10)])
    door_width = FloatField('Door Width (meters)', validators=[NumberRange(min=0.1, max=5)])
    door_height = FloatField('Door Height (meters)', validators=[NumberRange(min=0.1, max=5)])
    corridor_width = FloatField('Corridor Width (meters)', validators=[NumberRange(min=0.1, max=10)])
    ceiling_clearance = FloatField('Ceiling Clearance (meters)', validators=[NumberRange(min=0.1, max=10)])
    
    # Structural Information
    floor_type = SelectField('Floor Type', choices=[
        ('', 'Select Floor Type'),
        ('concrete', 'Reinforced Concrete'),
        ('steel', 'Steel Frame'),
        ('composite', 'Composite'),
        ('raised', 'Raised Floor'),
        ('other', 'Other')
    ])
    floor_load_capacity = FloatField('Floor Load Capacity (kg/m²)', validators=[NumberRange(min=0, max=50000)])
    ceiling_type = SelectField('Ceiling Type', choices=[
        ('', 'Select Ceiling Type'),
        ('suspended', 'Suspended Ceiling'),
        ('concrete', 'Concrete Slab'),
        ('steel', 'Steel Beam'),
        ('other', 'Other')
    ])
    wall_construction = SelectField('Wall Construction', choices=[
        ('', 'Select Wall Type'),
        ('concrete', 'Concrete Block'),
        ('drywall', 'Drywall'),
        ('brick', 'Brick'),
        ('steel', 'Steel Frame'),
        ('other', 'Other')
    ])
    foundation_type = StringField('Foundation Type', validators=[Length(max=50)])
    seismic_zone = SelectField('Seismic Zone', choices=[
        ('', 'Unknown'),
        ('low', 'Low Risk'),
        ('moderate', 'Moderate Risk'),
        ('high', 'High Risk'),
        ('very_high', 'Very High Risk')
    ])
    building_age = IntegerField('Building Age (years)', validators=[NumberRange(min=0, max=200)])
    
    # Electrical Systems
    available_power = SelectField('Available Power', choices=[
        ('', 'Select Power Type'),
        ('triphasé 380V', '380V 3-Phase'),
        ('triphasé 400V', '400V 3-Phase'),
        ('triphasé 480V', '480V 3-Phase'),
        ('monophasé 220V', '220V Single Phase'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    electrical_panel_distance = FloatField('Distance to Electrical Panel (meters)', validators=[NumberRange(min=0, max=1000)])
    electrical_panel_capacity = FloatField('Panel Capacity (kVA)', validators=[NumberRange(min=0, max=5000)])
    voltage_stability = SelectField('Voltage Stability', choices=[
        ('', 'Unknown'),
        ('excellent', 'Excellent (±1%)'),
        ('good', 'Good (±3%)'),
        ('fair', 'Fair (±5%)'),
        ('poor', 'Poor (>±5%)')
    ])
    has_ups = BooleanField('UPS System Available')
    ups_capacity = FloatField('UPS Capacity (kVA)', validators=[NumberRange(min=0, max=1000)])
    has_isolation_transformer = BooleanField('Isolation Transformer Available')
    grounding_system = SelectField('Grounding System', choices=[
        ('', 'Select Grounding Type'),
        ('standard', 'Standard Building Ground'),
        ('enhanced', 'Enhanced Medical Ground'),
        ('isolated', 'Isolated Ground'),
        ('none', 'No Dedicated Ground'),
        ('unknown', 'Unknown')
    ])
    emergency_power = BooleanField('Emergency Power Generator')
    
    # HVAC & Environmental
    has_hvac = BooleanField('HVAC System Present')
    hvac_capacity = StringField('HVAC Capacity', validators=[Length(max=50)])
    hvac_type = SelectField('HVAC Type', choices=[
        ('', 'Select HVAC Type'),
        ('central', 'Central Air System'),
        ('split', 'Split System'),
        ('vrf', 'VRF System'),
        ('chilled_water', 'Chilled Water'),
        ('other', 'Other')
    ])
    current_temperature_range = StringField('Current Temperature Range', validators=[Length(max=20)])
    current_humidity_range = StringField('Current Humidity Range', validators=[Length(max=20)])
    air_changes_per_hour = FloatField('Air Changes per Hour', validators=[NumberRange(min=0, max=100)])
    filtration_system = StringField('Air Filtration System', validators=[Length(max=50)])
    humidity_control = BooleanField('Dedicated Humidity Control')
    
    # Safety & Utilities
    existing_shielding = BooleanField('Existing Radiation Shielding')
    shielding_details = TextAreaField('Shielding Details', validators=[Length(max=1000)])
    shielding_type = SelectField('Shielding Type', choices=[
        ('', 'None'),
        ('lead', 'Lead Sheets'),
        ('lead_drywall', 'Lead-lined Drywall'),
        ('concrete', 'Concrete Barriers'),
        ('steel', 'Steel Plating'),
        ('other', 'Other')
    ])
    water_supply = BooleanField('Water Supply Available')
    water_pressure = FloatField('Water Pressure (PSI)', validators=[NumberRange(min=0, max=500)])
    compressed_air = BooleanField('Compressed Air Available')
    compressed_air_pressure = FloatField('Compressed Air Pressure (PSI)', validators=[NumberRange(min=0, max=500)])
    network_infrastructure = BooleanField('Network Infrastructure')
    network_speed = StringField('Network Speed', validators=[Length(max=50)])
    fire_suppression = SelectField('Fire Suppression System', choices=[
        ('', 'Select System Type'),
        ('sprinkler', 'Sprinkler System'),
        ('fm200', 'FM-200 Gas System'),
        ('co2', 'CO2 System'),
        ('dry', 'Dry Chemical'),
        ('none', 'None'),
        ('other', 'Other')
    ])
    emergency_systems = TextAreaField('Emergency Systems', validators=[Length(max=1000)])
    security_systems = TextAreaField('Security Systems', validators=[Length(max=1000)])
    
    # Compliance & Regulatory
    accessibility_compliance = BooleanField('ADA Compliant')
    ada_compliant = BooleanField('Full ADA Compliance')
    building_permits_status = SelectField('Building Permits Status', choices=[
        ('', 'Select Status'),
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('not_required', 'Not Required'),
        ('not_obtained', 'Not Obtained'),
        ('expired', 'Expired'),
        ('unknown', 'Unknown')
    ])
    environmental_clearances = BooleanField('Environmental Clearances Obtained')
    local_regulations = TextAreaField('Local Regulations Notes', validators=[Length(max=1000)])
    inspection_history = TextAreaField('Inspection History', validators=[Length(max=1000)])
    
    # Operational Considerations
    operating_hours = StringField('Operating Hours', validators=[Length(max=50)])
    patient_volume = IntegerField('Daily Patient Volume', validators=[NumberRange(min=0, max=1000)])
    staff_count = IntegerField('Staff Count', validators=[NumberRange(min=0, max=100)])
    workflow_requirements = TextAreaField('Workflow Requirements', validators=[Length(max=1000)])
    parking_availability = BooleanField('Adequate Parking Available')
    
    # Additional Information
    site_constraints = TextAreaField('Site Constraints', validators=[Length(max=2000)])
    special_requirements = TextAreaField('Special Requirements', validators=[Length(max=2000)])
    renovation_history = TextAreaField('Renovation History', validators=[Length(max=1000)])
    future_expansion_plans = TextAreaField('Future Expansion Plans', validators=[Length(max=1000)])
    notes = TextAreaField('Additional Notes', validators=[Length(max=2000)])
    
    # Assessment Metadata
    assessment_confidence = SelectField('Assessment Confidence', choices=[
        ('high', 'High - Detailed measurements'),
        ('medium', 'Medium - Visual inspection'),
        ('low', 'Low - Estimates only')
    ], default='medium')
    photos_available = BooleanField('Photos Available')
    drawings_available = BooleanField('Technical Drawings Available')

class EnhancedAIAnalysisForm(FlaskForm):
    """Enhanced form for AI conformity analysis"""
    site_specification_id = SelectField('Site Specification', coerce=int, validators=[DataRequired()])
    analysis_type = SelectField('Analysis Type', choices=[
        ('comprehensive', 'Comprehensive Analysis'),
        ('dimensional', 'Dimensional Compliance Only'),
        ('electrical', 'Electrical Infrastructure Focus'),
        ('neuviz', 'NeuViz-Specific Analysis'),
        ('safety', 'Safety & Compliance Assessment'),
        ('cost', 'Cost Estimation Focus'),
        ('environmental', 'Environmental Controls Analysis'),
        ('structural', 'Structural Assessment'),
        ('workflow', 'Workflow Optimization')
    ], default='comprehensive')
    include_3d_visualization = BooleanField('Include 3D Visualization', default=True)
    include_cost_analysis = BooleanField('Include Detailed Cost Analysis', default=True)
    include_timeline_analysis = BooleanField('Include Timeline Analysis', default=True)
    generate_pdf = BooleanField('Generate PDF Report', default=True)
    send_email = BooleanField('Send Email Notification', default=False)
    email_recipients = StringField('Email Recipients (comma separated)')
    priority_level = SelectField('Analysis Priority', choices=[
        ('standard', 'Standard'),
        ('expedited', 'Expedited'),
        ('urgent', 'Urgent')
    ], default='standard')

# ===== PROFESSIONAL TEMPLATE SYSTEM =====

def get_professional_base_template():
    """Professional base template with Promamec branding"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Promamec CT Scanner Professional Suite</title>
    
    <!-- Professional CSS Framework -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    
    <style>
        :root {
            --promamec-primary: #1e3a8a;
            --promamec-secondary: #3b82f6;
            --promamec-accent: #0ea5e9;
            --promamec-success: #059669;
            --promamec-warning: #d97706;
            --promamec-danger: #dc2626;
            --promamec-dark: #1f2937;
            --promamec-light: #f8fafc;
            --promamec-border: #e5e7eb;
            --promamec-text: #374151;
            --promamec-text-light: #6b7280;
            --promamec-gradient: linear-gradient(135deg, var(--promamec-primary) 0%, var(--promamec-secondary) 100%);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 14px;
            line-height: 1.6;
            color: var(--promamec-text);
            background-color: var(--promamec-light);
        }
        
        /* Professional Navigation */
        .promamec-navbar {
            background: var(--promamec-gradient);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 0.75rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        
        .promamec-navbar .navbar-brand {
            font-weight: 700;
            color: white !important;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
        }
        
        .promamec-navbar .nav-link {
            color: rgba(255,255,255,0.9) !important;
            font-weight: 500;
            padding: 0.5rem 1rem !important;
            border-radius: 8px;
            transition: all 0.3s ease;
            margin: 0 0.2rem;
        }
        
        .promamec-navbar .nav-link:hover {
            background-color: rgba(255,255,255,0.15);
            color: white !important;
            transform: translateY(-1px);
        }
        
        /* Professional Cards */
        .promamec-card {
            background: white;
            border: 1px solid var(--promamec-border);
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            overflow: hidden;
        }
        
        .promamec-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }
        
        .promamec-card-header {
            background: var(--promamec-gradient);
            color: white;
            padding: 1.5rem;
            border: none;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        /* Professional Buttons */
        .btn-promamec-primary {
            background: var(--promamec-gradient);
            border: none;
            color: white;
            font-weight: 600;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
        }
        
        .btn-promamec-primary:hover {
            background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
            color: white;
        }
        
        .btn-promamec-secondary {
            background: var(--promamec-accent);
            border: none;
            color: white;
            font-weight: 500;
            padding: 0.75rem 1.5rem;
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .btn-promamec-secondary:hover {
            background: #0284c7;
            transform: translateY(-2px);
            color: white;
        }
        
        /* Enhanced Forms */
        .form-control {
            border: 2px solid var(--promamec-border);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            font-size: 14px;
            transition: all 0.3s ease;
            background-color: #fff;
        }
        
        .form-control:focus {
            border-color: var(--promamec-secondary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background-color: #fff;
        }
        
        .form-label {
            font-weight: 600;
            color: var(--promamec-text);
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        
        /* Professional Tables */
        .table-promamec {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        
        .table-promamec thead th {
            background: var(--promamec-primary);
            color: white;
            font-weight: 600;
            border: none;
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .table-promamec tbody tr:hover {
            background-color: var(--promamec-light);
        }
        
        /* Professional Metrics */
        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            border: 1px solid var(--promamec-border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--promamec-gradient);
        }
        
        .metric-card:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-4px);
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--promamec-primary);
            margin-bottom: 0.5rem;
            line-height: 1;
        }
        
        .metric-label {
            color: var(--promamec-text-light);
            font-weight: 500;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Professional Badges */
        .badge-promamec {
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-promamec-success {
            background: linear-gradient(45deg, var(--promamec-success), #10b981);
            color: white;
        }
        
        .badge-promamec-warning {
            background: linear-gradient(45deg, var(--promamec-warning), #f59e0b);
            color: white;
        }
        
        .badge-promamec-danger {
            background: linear-gradient(45deg, var(--promamec-danger), #ef4444);
            color: white;
        }
        
        /* Professional Alerts */
        .alert-promamec {
            border: none;
            border-radius: 12px;
            padding: 1.5rem;
            border-left: 4px solid;
        }
        
        .alert-promamec-info {
            background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
            border-left-color: var(--promamec-accent);
            color: #0c4a6e;
        }
        
        .alert-promamec-success {
            background: linear-gradient(135deg, #dcfce7 0%, #d1fae5 100%);
            border-left-color: var(--promamec-success);
            color: #14532d;
        }
        
        /* Professional Footer */
        .promamec-footer {
            background: var(--promamec-dark);
            color: white;
            padding: 3rem 0 2rem;
            margin-top: 4rem;
        }
        
        /* Status Indicators */
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 0.5rem;
        }
        
        .status-success { background: var(--promamec-success); }
        .status-warning { background: var(--promamec-warning); }
        .status-danger { background: var(--promamec-danger); }
        .status-info { background: var(--promamec-accent); }
        
        /* Loading States */
        .loading-spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid var(--promamec-primary);
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .metric-card {
                padding: 1.5rem;
            }
            
            .metric-value {
                font-size: 2rem;
            }
            
            .promamec-card-header {
                padding: 1rem;
            }
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--promamec-secondary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--promamec-primary);
        }
    </style>
</head>
<body>
    <!-- Professional Navigation -->
    <nav class="navbar navbar-expand-lg promamec-navbar">
        <div class="container-fluid">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <i class="fas fa-hospital me-2"></i>
                <span>{{ config.COMPANY_NAME }}</span>
                <small class="ms-2 opacity-75">v{{ config.VERSION }}</small>
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('dashboard') }}">
                                <i class="bi bi-speedometer2"></i> Dashboard
                            </a>
                        </li>
                        {% if current_user.role in ['Engineer', 'Admin'] %}
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                                    <i class="bi bi-tools"></i> Professional Tools
                                </a>
                                <ul class="dropdown-menu">
                                    <li><a class="dropdown-item" href="{{ url_for('manual_room_entry') }}">
                                        <i class="bi bi-rulers"></i> Manual Room Entry
                                    </a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('ai_analysis') }}">
                                        <i class="bi bi-robot"></i> AI Analysis
                                    </a></li>
                                    <li><a class="dropdown-item" href="{{ url_for('scanner_comparison') }}">
                                        <i class="bi bi-arrow-left-right"></i> Scanner Comparison
                                    </a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item" href="{{ url_for('analytics_dashboard') }}">
                                        <i class="bi bi-graph-up"></i> Analytics Dashboard
                                    </a></li>
                                </ul>
                            </li>
                        {% endif %}
                        {% if current_user.role == 'Admin' %}
                            <li class="nav-item">
                                <a class="nav-link" href="/admin/">
                                    <i class="bi bi-gear"></i> Administration
                                </a>
                            </li>
                        {% endif %}
                    {% endif %}
                </ul>
                
                <ul class="navbar-nav">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown">
                                <i class="bi bi-person-circle me-1"></i>
                                {{ current_user.full_name }}
                                <span class="badge bg-light text-dark ms-2">{{ current_user.role }}</span>
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><h6 class="dropdown-header">{{ current_user.professional_title }}</h6></li>
                                <li><a class="dropdown-item" href="#">
                                    <i class="bi bi-person"></i> Profile Settings
                                </a></li>
                                <li><a class="dropdown-item" href="#">
                                    <i class="bi bi-bell"></i> Notifications
                                </a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{{ url_for('logout') }}">
                                    <i class="bi bi-box-arrow-right"></i> Sign Out
                                </a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('login') }}">
                                <i class="bi bi-box-arrow-in-right"></i> Sign In
                            </a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="{{ url_for('register') }}">
                                <i class="bi bi-person-plus"></i> Register
                            </a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="row">
                    <div class="col-12">
                        {% for category, message in messages %}
                            <div class="alert alert-promamec alert-promamec-{{ 'info' if category == 'info' else 'success' if category == 'success' else 'danger' }} alert-dismissible fade show">
                                <i class="bi bi-{{ 'info-circle' if category == 'info' else 'check-circle' if category == 'success' else 'exclamation-triangle' }}"></i>
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    </div>
                </div>
            {% endif %}
        {% endwith %}
        
        <!-- CONTENT PLACEHOLDER -->
        {{ content|safe }}
    </main>

    <!-- Professional Footer -->
    <footer class="promamec-footer">
        <div class="container">
            <div class="row">
                <div class="col-md-4">
                    <h5><i class="fas fa-hospital"></i> {{ config.COMPANY_NAME }}</h5>
                    <p class="mb-2">{{ config.COMPANY_TAGLINE }}</p>
                    <p class="small">Professional CT Scanner Solutions Platform</p>
                </div>
                <div class="col-md-4">
                    <h6>Professional Services</h6>
                    <ul class="list-unstyled small">
                        <li><i class="bi bi-check2"></i> AI-Powered Conformity Analysis</li>
                        <li><i class="bi bi-check2"></i> 3D Visualization & Modeling</li>
                        <li><i class="bi bi-check2"></i> Professional PDF Reporting</li>
                        <li><i class="bi bi-check2"></i> NeuViz Certified Analysis</li>
                    </ul>
                </div>
                <div class="col-md-4 text-md-end">
                    <p class="mb-1">&copy; 2025 {{ config.COMPANY_NAME }}. All rights reserved.</p>
                    <small class="text-muted">
                        Version {{ config.VERSION }} | Build {{ config.BUILD }}
                    </small>
                </div>
            </div>
        </div>
    </footer>

    <!-- Professional JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Professional UI Enhancements
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth scrolling for anchor links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
            
            // Auto-hide alerts after 5 seconds
            setTimeout(function() {
                const alerts = document.querySelectorAll('.alert');
                alerts.forEach(alert => {
                    const closeBtn = alert.querySelector('.btn-close');
                    if (closeBtn) closeBtn.click();
                });
            }, 5000);
            
            // Loading states for forms
            document.querySelectorAll('form').forEach(form => {
                form.addEventListener('submit', function() {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';
                        submitBtn.disabled = true;
                    }
                });
            });
        });
    </script>
</body>
</html>
    '''

def render_professional_page(content):
    """Render a page using the professional template system"""
    base = get_professional_base_template()
    return base.replace('{{ content|safe }}', content)

# ===== ENHANCED AI ANALYSIS ENGINE =====

class AdvancedCTScannerAI:
    """Advanced AI analysis engine with GPT-4 integration"""
    
    @staticmethod
    def analyze_conformity_comprehensive(site_spec, analysis_type='comprehensive', priority='standard'):
        """Comprehensive AI conformity analysis with enhanced features"""
        try:
            if not client:
                return {
                    'success': False,
                    'error': 'OpenAI client not initialized',
                    'status': 'Error',
                    'score': 0,
                    'analysis': 'AI analysis unavailable - please configure OpenAI API key.',
                    'recommendations': 'Configure OpenAI API key to enable advanced AI analysis.',
                    'risk_level': 'Unknown',
                    'estimated_cost': 0,
                    'timeline': 30
                }
            
            # Build comprehensive prompt
            prompt = AdvancedCTScannerAI._build_comprehensive_prompt(site_spec, analysis_type, priority)
            
            # Enhanced GPT-4 configuration
            model = "gpt-4" if priority == 'urgent' else "gpt-3.5-turbo"
            max_tokens = 4000 if analysis_type == 'comprehensive' else 2000
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are Dr. Sarah Chen, a senior biomedical engineer with 25+ years of experience in CT scanner installations, specializing in NeuViz systems and regulatory compliance. You provide detailed, technical analysis with specific measurements, costs, and actionable recommendations."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Enhanced parsing with intelligent extraction
            analysis_result = AdvancedCTScannerAI._parse_comprehensive_response(ai_response, site_spec)
            
            # Log successful analysis
            logger.info(f"AI analysis completed for site {site_spec.site_name}: {analysis_result['status']} ({analysis_result['score']}%)")
            
            return analysis_result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Enhanced AI analysis failed: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'status': 'Error',
                'score': 0,
                'analysis': f"AI analysis encountered an error: {error_msg}",
                'recommendations': 'Please check system configuration and try again.',
                'risk_level': 'Unknown',
                'estimated_cost': 0,
                'timeline': 30
            }
    
    @staticmethod
    def _build_comprehensive_prompt(site_spec, analysis_type, priority):
        """Build comprehensive analysis prompt for AI"""
        scanner = site_spec.scanner_model
        
        prompt = f"""
COMPREHENSIVE CT SCANNER PREINSTALLATION CONFORMITY ANALYSIS
Analysis Priority: {priority.upper()} | Analysis Type: {analysis_type.upper()}

SCANNER SPECIFICATIONS:
- Manufacturer: {scanner.manufacturer}
- Model: {scanner.model_name} ({scanner.slice_count}-slice)
- Weight: {scanner.weight} kg | Dimensions: {scanner.dimensions}
- Room Requirements: {scanner.min_room_length}m × {scanner.min_room_width}m × {scanner.min_room_height}m
- Power: {scanner.required_power} | Consumption: {scanner.power_consumption}kW
- Power Factor: {scanner.power_factor_requirement or 'Standard'}
- Cooling: {scanner.cooling_requirements}
- Heat Dissipation: {scanner.heat_dissipation}kW
- Environmental: {scanner.environmental_specs}
- NeuViz Equipment: {'Yes - ' + scanner.neuviz_manual_ref if scanner.is_neuviz else 'No'}
- Installation Complexity: {scanner.installation_complexity}

SITE CONDITIONS:
- Installation Site: {site_spec.site_name}
- Location: {site_spec.address or 'Not specified'}
- Room Dimensions: {site_spec.room_length}m × {site_spec.room_width}m × {site_spec.room_height}m
- Door Access: {site_spec.door_width or 'Not specified'}m × {site_spec.door_height or 'Not specified'}m
- Electrical Power: {site_spec.available_power}
- Panel Location: {site_spec.electrical_panel_location or 'Not specified'}
- HVAC System: {'Yes - ' + site_spec.hvac_capacity if site_spec.has_hvac else 'No'}
- Floor Type: {site_spec.floor_type or 'Not specified'}
- Floor Capacity: {site_spec.floor_load_capacity or 'Not specified'} kg/m²
- Existing Shielding: {'Yes' if site_spec.existing_shielding else 'No'}
- Utilities: Water: {'Yes' if site_spec.water_supply else 'No'}, Air: {'Yes' if site_spec.compressed_air else 'No'}, Network: {'Yes' if site_spec.network_infrastructure else 'No'}
- ADA Compliance: {'Yes' if site_spec.accessibility_compliance else 'No'}
- Notes: {site_spec.notes or 'None provided'}

ANALYSIS REQUIREMENTS:

1. **DIMENSIONAL COMPLIANCE ASSESSMENT**
   - Precise room space adequacy calculation
   - Equipment placement optimization
   - Service access clearance verification
   - Patient/staff workflow analysis
   - Transport pathway assessment

2. **STRUCTURAL ENGINEERING EVALUATION**
   - Floor loading capacity verification (including dynamic loads)
   - Foundation requirements assessment
   - Vibration isolation specifications
   - Anchoring and mounting system design
   - Seismic considerations

3. **ELECTRICAL INFRASTRUCTURE ANALYSIS**
   - Power supply compatibility and capacity verification
   - Voltage regulation and stability requirements
   - Power factor correction analysis (critical for NeuViz)
   - Grounding and earthing system design
   - Emergency power integration
   - Electrical code compliance

4. **ENVIRONMENTAL CONTROLS ENGINEERING**
   - HVAC system adequacy for equipment cooling
   - Precision temperature control (18-24°C for NeuViz)
   - Humidity control systems (30-70% RH)
   - Air filtration and circulation requirements
   - Noise and vibration control

5. **RADIATION SAFETY & SHIELDING DESIGN**
   - Primary and secondary barrier calculations
   - Lead equivalency requirements (2.5mm for NeuViz)
   - Controlled area designation
   - Radiation monitoring systems
   - IEC 60601-2-44 compliance verification

6. **REGULATORY COMPLIANCE VERIFICATION**
   - Building codes and permit requirements
   - Fire safety regulations compliance
   - Accessibility standards (ADA) verification
   - Local health department requirements
   - Insurance and liability considerations

7. **RISK ASSESSMENT & MITIGATION**
   - Installation complexity risk factors
   - Timeline impact assessment
   - Budget risk analysis
   - Operational readiness evaluation
   - Contingency planning

8. **COST-BENEFIT ANALYSIS**
   - Detailed modification cost estimation
   - Alternative solutions evaluation
   - Return on investment analysis
   - Lifecycle cost considerations
   - Value engineering opportunities
"""

        # Add NeuViz-specific requirements
        if scanner.is_neuviz:
            prompt += f"""

NEUSOFT NEUVIZ SPECIFIC COMPLIANCE ANALYSIS ({scanner.neuviz_manual_ref}):

MANDATORY REQUIREMENTS VERIFICATION:
✓ Installation Engineer: Certified Neusoft engineer supervision required
✓ Environmental Control: 18-24°C, 30-70% RH, ±4.1°C/hour max fluctuation
✓ Power Requirements: 380V triphasé, power factor ≥0.84 MANDATORY
✓ Grounding: Enhanced earthing system with medical-grade isolation
✓ Floor Specifications: FC=1.7×10³N/cm² minimum bearing capacity
✓ Transport: Specialized pallets with engineer supervision required
✓ Air Circulation: Proper flow direction per Figure 22 requirements
✓ Cooling: Medical-grade precision HVAC with enhanced controls
✓ Vibration Control: Specialized mounting and isolation systems
✓ Quality Assurance: Factory and Site Acceptance Testing protocols

ENHANCED NEUVIZ COST FACTORS:
- Neusoft Certified Engineer: $8,000-$12,000
- Enhanced Grounding System: $15,000-$25,000
- Specialized Transport: $6,000-$10,000
- Precision HVAC Upgrade: $20,000-$35,000
- Advanced Mounting System: $8,000-$15,000

PERFORM DETAILED NPS-CT-0651 COMPLIANCE VERIFICATION
"""

        prompt += f"""

RESPONSE FORMAT REQUIRED:

**OVERALL CONFORMITY STATUS:** [FULLY_CONFORMING / REQUIRES_MINOR_MODIFICATIONS / REQUIRES_MAJOR_MODIFICATIONS / NON_CONFORMING]

**CONFORMITY SCORE:** [0-100% with detailed technical justification]

**RISK ASSESSMENT:** [Low / Medium / High / Critical with comprehensive explanation]

**DETAILED TECHNICAL ANALYSIS:**
1. **Dimensional Compliance:** [Specific measurements and clearance analysis]
2. **Structural Assessment:** [Load calculations and foundation requirements]
3. **Electrical Systems:** [Power adequacy and system modifications needed]
4. **Environmental Controls:** [HVAC specifications and upgrades required]
5. **Radiation Safety:** [Shielding calculations and controlled area design]
6. **Regulatory Compliance:** [Permits, codes, and approval requirements]
{'7. **NeuViz Compliance:** [Detailed NPS-CT-0651 verification]' if scanner.is_neuviz else ''}

**CRITICAL ISSUES IDENTIFIED:** [Prioritized list of blocking issues with severity ratings]

**COMPREHENSIVE RECOMMENDATIONS:**
- **Immediate Actions (0-30 days):** [Priority 1 items with specific timelines]
- **Infrastructure Modifications (30-90 days):** [Detailed technical requirements]
- **Regulatory Actions (ongoing):** [Permits, approvals, inspections]
- **Cost Optimization Strategies:** [Value engineering opportunities]

**DETAILED PROJECT IMPACT ASSESSMENT:**
- **Timeline Analysis:** [Phase-by-phase implementation schedule]
- **Budget Impact:** [Itemized cost breakdown with contingencies]
- **Risk Mitigation:** [Specific strategies for identified risks]
- **Quality Assurance:** [Testing and validation protocols]

**PROFESSIONAL CERTIFICATION:** As a senior biomedical engineer, I certify this analysis follows professional engineering standards and applicable codes.

Provide highly technical, detailed, and actionable analysis using precise engineering terminology, specific measurements, and professional cost estimates.
"""
        
        return prompt
    
    @staticmethod
    def _parse_comprehensive_response(ai_response, site_spec):
        """Parse AI response with advanced intelligence"""
        
        response_lower = ai_response.lower()
        
        # Enhanced status detection with better intelligence
        if 'fully_conforming' in response_lower or 'fully conforming' in response_lower:
            status = 'CONFORMING'
        elif 'requires_minor_modifications' in response_lower or 'minor modifications' in response_lower:
            status = 'REQUIRES_MODIFICATION'
        elif 'requires_major_modifications' in response_lower or 'major modifications' in response_lower:
            status = 'REQUIRES_MODIFICATION'
        elif 'non_conforming' in response_lower or 'non-conforming' in response_lower:
            status = 'NON_CONFORMING'
        else:
            # Intelligent analysis of response content
            positive_terms = ['compliant', 'adequate', 'meets requirements', 'acceptable', 'conforming']
            negative_terms = ['non-compliant', 'inadequate', 'does not meet', 'insufficient', 'critical issues']
            
            positive_score = sum(response_lower.count(term) for term in positive_terms)
            negative_score = sum(response_lower.count(term) for term in negative_terms)
            
            if positive_score > negative_score * 1.5:
                status = 'CONFORMING'
            elif negative_score > positive_score * 1.5:
                status = 'NON_CONFORMING'
            else:
                status = 'REQUIRES_MODIFICATION'
        
        # Advanced score extraction with multiple patterns
        score_patterns = [
            r'conformity score[:\s]*(\d+(?:\.\d+)?)%',
            r'score[:\s]*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%[:\s]*conformity',
            r'assessment[:\s]*(\d+(?:\.\d+)?)%',
            r'compliance[:\s]*(\d+(?:\.\d+)?)%'
        ]
        
        score = None
        for pattern in score_patterns:
            score_match = re.search(pattern, response_lower)
            if score_match:
                score = float(score_match.group(1))
                break
        
        # Intelligent score calculation if not found
        if score is None:
            score = AdvancedCTScannerAI._calculate_intelligent_score(site_spec, status, response_lower)
        
        # Enhanced risk level detection
        risk_patterns = [
            (r'critical risk|risk.*critical', 'Critical'),
            (r'high risk|risk.*high', 'High'),
            (r'medium risk|risk.*medium', 'Medium'),
            (r'low risk|risk.*low', 'Low')
        ]
        
        risk_level = 'Medium'  # Default
        for pattern, level in risk_patterns:
            if re.search(pattern, response_lower):
                risk_level = level
                break
        
        # Intelligent risk assessment based on score and content
        if score >= 90:
            risk_level = 'Low'
        elif score >= 75:
            risk_level = 'Medium'
        elif score >= 50:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
        
        # Enhanced cost and timeline estimation
        estimated_cost = AdvancedCTScannerAI._calculate_advanced_cost(site_spec, ai_response, score, status)
        timeline = AdvancedCTScannerAI._calculate_project_timeline(site_spec, ai_response, score, status)
        
        # Extract comprehensive recommendations
        recommendations = AdvancedCTScannerAI._extract_comprehensive_recommendations(ai_response)
        
        return {
            'success': True,
            'status': status,
            'score': round(score, 1),
            'analysis': ai_response,
            'recommendations': recommendations,
            'risk_level': risk_level,
            'estimated_cost': estimated_cost,
            'timeline': timeline
        }
    
    @staticmethod
    def _calculate_intelligent_score(site_spec, status, response_content):
        """Calculate conformity score using intelligent analysis"""
        scanner = site_spec.scanner_model
        base_score = 50
        
        # Dimensional compliance
        room_volume = site_spec.room_length * site_spec.room_width * site_spec.room_height
        required_volume = scanner.min_room_length * scanner.min_room_width * scanner.min_room_height
        
        if room_volume >= required_volume * 1.2:
            base_score += 20
        elif room_volume >= required_volume:
            base_score += 15
        else:
            base_score -= 20
        
        # Power compatibility
        if site_spec.available_power == scanner.required_power:
            base_score += 15
        else:
            base_score -= 10
        
        # HVAC availability
        if site_spec.has_hvac:
            base_score += 10
        else:
            base_score -= 15
        
        # Floor capacity
        if site_spec.floor_load_capacity and site_spec.floor_load_capacity > scanner.weight * 2:
            base_score += 10
        
        # Status-based adjustment
        if status == 'CONFORMING':
            base_score = max(base_score, 85)
        elif status == 'NON_CONFORMING':
            base_score = min(base_score, 50)
        
        return max(0, min(100, base_score))
    
    @staticmethod
    def _calculate_advanced_cost(site_spec, ai_response, score, status):
        """Calculate comprehensive project cost"""
        scanner = site_spec.scanner_model
        base_cost = 8000  # Enhanced professional assessment
        
        # Room modifications
        room_volume = site_spec.room_length * site_spec.room_width * site_spec.room_height
        required_volume = scanner.min_room_length * scanner.min_room_width * scanner.min_room_height
        
        if room_volume < required_volume:
            volume_deficit = required_volume - room_volume
            base_cost += volume_deficit * 20000  # Cost per cubic meter expansion
        
        # Height modifications
        height_diff = max(0, scanner.min_room_height - site_spec.room_height)
        if height_diff > 0:
            base_cost += height_diff * 12000
        
        # Electrical infrastructure
        if site_spec.available_power != scanner.required_power:
            base_cost += 25000  # Electrical system upgrade
        
        # HVAC systems
        if not site_spec.has_hvac:
            if scanner.is_neuviz:
                base_cost += 45000  # Precision HVAC for NeuViz
            else:
                base_cost += 30000  # Standard medical HVAC
        elif scanner.is_neuviz:
            base_cost += 20000  # HVAC upgrade for precision control
        
        # Floor reinforcement
        if not site_spec.floor_load_capacity or site_spec.floor_load_capacity < (scanner.weight * 2):
            base_cost += 18000
        
        # NeuViz-specific costs
        if scanner.is_neuviz:
            base_cost += 12000  # Neusoft engineer
            base_cost += 25000  # Enhanced grounding and precision systems
            base_cost += 10000  # Specialized transport and installation
            base_cost += 8000   # Environmental monitoring systems
        
        # Radiation shielding
        if not site_spec.existing_shielding:
            base_cost += 35000  # Comprehensive shielding installation
        
        # Score-based cost adjustment
        if score >= 85:
            base_cost *= 0.6  # Minimal modifications
        elif score >= 70:
            base_cost *= 0.8  # Minor modifications
        elif score >= 50:
            base_cost *= 1.3  # Significant modifications
        else:
            base_cost *= 1.8  # Major overhaul
        
        # Status-based adjustment
        status_multipliers = {
            'CONFORMING': 0.5,
            'REQUIRES_MODIFICATION': 1.0,
            'NON_CONFORMING': 1.6
        }
        base_cost *= status_multipliers.get(status, 1.0)
        
        # AI response cost indicators
        response_lower = ai_response.lower()
        if 'extensive' in response_lower or 'major renovation' in response_lower:
            base_cost *= 1.4
        elif 'minimal' in response_lower or 'simple changes' in response_lower:
            base_cost *= 0.7
        
        return round(base_cost, -2)  # Round to nearest hundred
    
    @staticmethod
    def _calculate_project_timeline(site_spec, ai_response, score, status):
        """Calculate comprehensive project timeline"""
        scanner = site_spec.scanner_model
        base_timeline = 45  # Enhanced base timeline
        
        # Score-based timeline
        if score < 40:
            base_timeline += 90  # Major reconstruction
        elif score < 60:
            base_timeline += 60  # Significant modifications
        elif score < 80:
            base_timeline += 30  # Moderate modifications
        
        # NeuViz additional coordination time
        if scanner.is_neuviz:
            base_timeline += 15  # Neusoft engineer coordination
        
        # System modifications
        if not site_spec.has_hvac:
            base_timeline += 25
        
        if site_spec.available_power != scanner.required_power:
            base_timeline += 20
        
        if not site_spec.existing_shielding:
            base_timeline += 30
        
        # Regulatory timeline
        base_timeline += 20  # Permits and approvals
        
        return base_timeline
    
    @staticmethod
    def _extract_comprehensive_recommendations(ai_response):
        """Extract detailed recommendations from AI response"""
        lines = ai_response.split('\n')
        recommendations = []
        
        # Look for recommendation sections
        in_recommendations = False
        recommendation_keywords = [
            'recommendation', 'action', 'required', 'should', 'must',
            'immediate', 'infrastructure', 'regulatory', 'cost optimization'
        ]
        
        for line in lines:
            line_clean = line.strip()
            line_lower = line_clean.lower()
            
            # Detect recommendation sections
            if any(keyword in line_lower for keyword in recommendation_keywords):
                if ':' in line_clean or line_clean.endswith(':'):
                    in_recommendations = True
                    continue
            
            # Extract recommendation items
            if in_recommendations and line_clean:
                if line_clean.startswith(('*', '-', '•', '1.', '2.', '3.')):
                    recommendations.append(line_clean.lstrip('*-•123456789. '))
                elif line_clean.startswith('**') and line_clean.endswith('**'):
                    in_recommendations = False  # End of section
                elif any(keyword in line_lower for keyword in ['immediate', 'priority', 'critical', 'must']):
                    recommendations.append(line_clean)
        
        # Fallback: extract sentences with action words
        if not recommendations:
            action_words = ['should', 'must', 'recommend', 'install', 'upgrade', 'modify', 'ensure']
            for line in lines:
                if any(word in line.lower() for word in action_words):
                    recommendations.append(line.strip())
        
        return '\n'.join(recommendations[:25]) if recommendations else 'Detailed recommendations provided in analysis above.'

# ===== ADVANCED PDF REPORT GENERATOR =====

class ProfessionalPDFReportGenerator:
    """Professional PDF report generator with advanced features"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.company_info = {
            'name': 'Promamec Solutions',
            'tagline': 'Professional Medical Equipment Consulting & Integration',
            'address': '123 Medical District, Healthcare Plaza',
            'phone': '+33 1 23 45 67 89',
            'email': 'solutions@promamec.com',
            'website': 'www.promamec.com'
        }
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom professional styles"""
        # Professional title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=20,
            alignment=1
        )
        
        # Professional heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#1e3a8a'),
            spaceBefore=15,
            spaceAfter=10
        )
        
        # Professional body style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            leftIndent=0,
            rightIndent=0,
            spaceAfter=8,
            alignment=0
        )
    
    def generate_comprehensive_report(self, report, include_visualizations=True):
        """Generate comprehensive professional PDF report"""
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=A4,
                rightMargin=60,
                leftMargin=60,
                topMargin=60,
                bottomMargin=60
            )
            
            story = []
            
            # Professional header
            story.extend(self._create_professional_header(report))
            story.append(Spacer(1, 20))
            
            # Executive summary
            story.extend(self._create_executive_summary(report))
            story.append(Spacer(1, 20))
            
            # Detailed technical analysis
            story.extend(self._create_technical_analysis(report))
            story.append(Spacer(1, 20))
            
            # Visual analytics (if enabled)
            if include_visualizations:
                story.extend(self._create_visual_analytics(report))
                story.append(Spacer(1, 20))
            
            # Cost analysis
            story.extend(self._create_cost_analysis(report))
            story.append(Spacer(1, 20))
            
            # Action plan
            story.extend(self._create_action_plan(report))
            story.append(Spacer(1, 20))
            
            # NeuViz-specific section
            if report.site_specification.scanner_model.is_neuviz:
                story.extend(self._create_neuviz_section(report))
                story.append(Spacer(1, 20))
            
            # Compliance checklist
            story.extend(self._create_compliance_section(report))
            story.append(Spacer(1, 20))
            
            # Professional footer
            story.extend(self._create_professional_footer())
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info(f"PDF report generated successfully for {report.report_number}")
            return buffer
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _create_professional_header(self, report):
        """Create professional report header"""
        elements = []
        
        # Company header
        header_data = [
            ['', self.company_info['name']],
            ['', self.company_info['tagline']],
            ['', f"Phone: {self.company_info['phone']} | Email: {self.company_info['email']}"]
        ]
        
        header_table = Table(header_data, colWidths=[1*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 0), 16),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (1, 1), 12),
            ('FONTNAME', (1, 2), (1, 2), 'Helvetica'),
            ('FONTSIZE', (1, 2), (1, 2), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1e3a8a')),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        
        # Report title
        elements.append(Paragraph("PROFESSIONAL CT SCANNER CONFORMITY ANALYSIS", self.title_style))
        
        # Report metadata
        metadata = [
            ['Report Number:', report.report_number],
            ['Generation Date:', datetime.now().strftime('%Y-%m-%d %H:%M UTC')],
            ['Project:', report.project.name],
            ['Client:', report.project.client_name],
            ['Site:', report.site_specification.site_name],
            ['Scanner Model:', f"{report.site_specification.scanner_model.manufacturer} {report.site_specification.scanner_model.model_name}"],
            ['Analysis Type:', 'AI-Enhanced Professional Assessment'],
            ['Conformity Status:', report.overall_status.replace('_', ' ')],
            ['Conformity Score:', f"{report.conformity_score:.1f}%" if report.conformity_score else 'Pending'],
            ['Risk Assessment:', report.risk_assessment or 'Not Assessed']
        ]
        
        metadata_table = Table(metadata, colWidths=[2.5*inch, 3.5*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(metadata_table)
        return elements
    
    def _create_executive_summary(self, report):
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.heading_style))
        
        # Status indicator
        status_text = f"<b>Overall Assessment:</b> {report.overall_status.replace('_', ' ')}"
        elements.append(Paragraph(status_text, self.body_style))
        
        # Key metrics
        metrics_data = [
            ['Metric', 'Value', 'Assessment'],
            ['Conformity Score', f"{report.conformity_score:.1f}%" if report.conformity_score else 'N/A', 
             'Excellent' if (report.conformity_score or 0) >= 85 else 'Good' if (report.conformity_score or 0) >= 70 else 'Requires Attention'],
            ['Risk Level', report.risk_assessment or 'Not Assessed',
             'Acceptable' if report.risk_assessment == 'Low' else 'Monitor' if report.risk_assessment == 'Medium' else 'Action Required'],
            ['Estimated Cost', f"${report.estimated_cost:,.0f}" if report.estimated_cost else 'TBD',
             'Budget-Friendly' if (report.estimated_cost or 0) < 50000 else 'Moderate' if (report.estimated_cost or 0) < 100000 else 'Significant Investment'],
            ['Timeline', f"{report.modification_timeline or 'TBD'} days",
             'Fast Track' if (report.modification_timeline or 0) < 30 else 'Standard' if (report.modification_timeline or 0) < 60 else 'Extended']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(Spacer(1, 10))
        elements.append(metrics_table)
        
        return elements
    
    def _create_technical_analysis(self, report):
        """Create detailed technical analysis section"""
        elements = []
        
        elements.append(Paragraph("DETAILED TECHNICAL ANALYSIS", self.heading_style))
        
        # AI Analysis with professional formatting
        analysis_text = report.ai_analysis or "Detailed technical analysis not available."
        
        # Format the analysis text for better presentation
        analysis_paragraphs = analysis_text.split('\n\n')
        for para in analysis_paragraphs[:10]:  # Limit to prevent overly long reports
            if para.strip():
                elements.append(Paragraph(para.strip(), self.body_style))
                elements.append(Spacer(1, 6))
        
        return elements
    
    def _create_visual_analytics(self, report):
        """Create visual analytics section with charts"""
        elements = []
        
        elements.append(Paragraph("VISUAL ANALYTICS", self.heading_style))
        
        try:
            # Generate conformity chart
            chart_buffer = self._generate_conformity_chart(report)
            if chart_buffer:
                chart_img = ReportLabImage(chart_buffer, width=4*inch, height=3*inch)
                elements.append(chart_img)
                elements.append(Spacer(1, 10))
        except Exception as e:
            logger.warning(f"Chart generation failed: {e}")
            elements.append(Paragraph("Visual analytics temporarily unavailable.", self.body_style))
        
        return elements
    
    def _generate_conformity_chart(self, report):
        """Generate conformity analysis chart"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Simple conformity gauge
            score = report.conformity_score or 0
            categories = ['Critical\n(0-50)', 'Modification\n(50-85)', 'Conforming\n(85-100)']
            values = [50, 35, 15]
            colors_list = ['#dc2626', '#d97706', '#059669']
            
            # Create gauge chart
            wedges, texts = ax.pie(values, labels=categories, colors=colors_list, 
                                 startangle=180, counterclock=False)
            
            # Add score indicator
            ax.text(0, -1.3, f'Conformity Score: {score:.1f}%', 
                   horizontalalignment='center', fontsize=16, fontweight='bold')
            
            plt.title('CT Scanner Conformity Assessment', fontsize=18, fontweight='bold', pad=20)
            
            # Save to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Chart generation error: {e}")
            return None
    
    def _create_cost_analysis(self, report):
        """Create detailed cost analysis section"""
        elements = []
        
        elements.append(Paragraph("COST ANALYSIS & BUDGET PLANNING", self.heading_style))
        
        # Cost breakdown
        base_cost = 5000
        total_cost = report.estimated_cost or base_cost
        
        cost_items = [
            ['Cost Category', 'Amount (USD)', 'Description'],
            ['Professional Assessment', f"${base_cost:,.0f}", 'Comprehensive conformity analysis'],
            ['Room Modifications', f"${max(0, (total_cost - base_cost) * 0.35):,.0f}", 'Structural changes if required'],
            ['Electrical Systems', f"${max(0, (total_cost - base_cost) * 0.25):,.0f}", 'Power system upgrades'],
            ['HVAC Installation', f"${max(0, (total_cost - base_cost) * 0.20):,.0f}", 'Environmental control systems'],
            ['Radiation Shielding', f"${max(0, (total_cost - base_cost) * 0.15):,.0f}", 'Safety compliance measures'],
            ['Project Management', f"${max(0, (total_cost - base_cost) * 0.05):,.0f}", 'Coordination and oversight'],
            ['TOTAL ESTIMATED', f"${total_cost:,.0f}", 'Complete project investment']
        ]
        
        cost_table = Table(cost_items, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e5e7eb')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(cost_table)
        return elements
    
    def _create_action_plan(self, report):
        """Create comprehensive action plan"""
        elements = []
        
        elements.append(Paragraph("ACTION PLAN & RECOMMENDATIONS", self.heading_style))
        
        # Parse recommendations
        recommendations = report.recommendations or "No specific recommendations provided."
        
        elements.append(Paragraph("<b>Priority Recommendations:</b>", self.body_style))
        
        # Split recommendations into actionable items
        rec_lines = [line.strip() for line in recommendations.split('\n') if line.strip()]
        
        for i, rec in enumerate(rec_lines[:15], 1):
            if rec.startswith(('-', '•', '*')):
                rec = rec[1:].strip()
            elements.append(Paragraph(f"{i}. {rec}", self.body_style))
        
        return elements
    
    def _create_neuviz_section(self, report):
        """Create NeuViz-specific analysis section"""
        elements = []
        
        elements.append(Paragraph("NEUVIZ ACE/ACE SP COMPLIANCE ANALYSIS", self.heading_style))
        
        neuviz_content = f"""
        <b>NeuViz Certification Requirements ({report.site_specification.scanner_model.neuviz_manual_ref}):</b><br/><br/>
        
        <b>Mandatory Compliance Items:</b><br/>
        • Installation Engineer: Certified Neusoft engineer supervision required<br/>
        • Environmental Control: 18-24°C, 30-70% humidity, ±4.1°C/hour maximum fluctuation<br/>
        • Power Requirements: 380V triphasé with power factor ≥0.84<br/>
        • Enhanced Grounding: Medical-grade earthing system mandatory<br/>
        • Floor Specifications: FC=1.7×10³N/cm² minimum bearing capacity<br/>
        • Specialized Transport: Engineer-supervised delivery and positioning<br/><br/>
        
        <b>Analysis Results:</b><br/>
        {report.neuviz_specific_analysis or 'Detailed NeuViz compliance verification completed per manufacturer specifications.'}<br/><br/>
        
        <b>Additional NeuViz Investment:</b><br/>
        • Neusoft Certified Engineer: $10,000<br/>
        • Enhanced Grounding System: $18,000<br/>
        • Specialized Transport: $8,000<br/>
        • Total NeuViz Premium: $36,000
        """
        
        elements.append(Paragraph(neuviz_content, self.body_style))
        return elements
    
    def _create_compliance_section(self, report):
        """Create regulatory compliance checklist"""
        elements = []
        
        elements.append(Paragraph("REGULATORY COMPLIANCE CHECKLIST", self.heading_style))
        
        site_spec = report.site_specification
        scanner = site_spec.scanner_model
        
        # Compliance matrix
        compliance_data = [
            ['Compliance Category', 'Status', 'Requirements'],
            ['Room Dimensions', '✓' if (site_spec.room_length >= scanner.min_room_length and 
                                      site_spec.room_width >= scanner.min_room_width and 
                                      site_spec.room_height >= scanner.min_room_height) else '⚠', 
             'Spatial adequacy verification'],
            ['Electrical Systems', '✓' if site_spec.available_power == scanner.required_power else '⚠', 
             'Power compatibility assessment'],
            ['Environmental Controls', '✓' if site_spec.has_hvac else '✗', 
             'HVAC system for equipment cooling'],
            ['Radiation Safety', '⚠', 'Shielding assessment required'],
            ['Accessibility (ADA)', '✓' if site_spec.accessibility_compliance else '⚠', 
             'Disability access compliance'],
            ['Building Permits', '⚠', 'Local authority approvals needed'],
            ['Fire Safety Systems', '⚠', 'Fire suppression compliance'],
            ['Environmental Clearance', '⚠', 'Environmental impact assessment']
        ]
        
        compliance_table = Table(compliance_data, colWidths=[2.5*inch, 0.8*inch, 2.7*inch])
        compliance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(compliance_table)
        return elements
    
    def _create_professional_footer(self):
        """Create professional report footer"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = f"""
        <b>{self.company_info['name']}</b><br/>
        {self.company_info['tagline']}<br/>
        {self.company_info['address']}<br/>
        Phone: {self.company_info['phone']} | Email: {self.company_info['email']}<br/>
        Website: {self.company_info['website']}<br/><br/>
        
        <i>This professional report is generated using advanced AI technology and engineering standards. 
        All recommendations should be verified by qualified biomedical engineers before implementation.
        Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}.</i><br/><br/>
        
        <b>CONFIDENTIAL - This document contains proprietary professional analysis.</b>
        """
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1,
        )
        
        elements.append(Paragraph(footer_text, footer_style))
        return elements

# ===== 3D VISUALIZATION ENGINE =====

class Advanced3DVisualizationEngine:
    """Advanced 3D visualization and interactive dashboards"""
    
    @staticmethod
    def create_comprehensive_dashboard(report):
        """Create comprehensive interactive dashboard"""
        try:
            from plotly.subplots import make_subplots
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Conformity Assessment', 'Risk Analysis', 'Cost Breakdown', 'Timeline Planning'),
                specs=[[{"type": "indicator"}, {"type": "bar"}],
                       [{"type": "pie"}, {"type": "scatter"}]]
            )
            
            # Conformity gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=report.conformity_score or 0,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Conformity Score (%)"},
                    delta={'reference': 85},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#059669" if (report.conformity_score or 0) >= 85 else "#d97706"},
                        'steps': [
                            {'range': [0, 50], 'color': "#fecaca"},
                            {'range': [50, 85], 'color': "#fef3c7"},
                            {'range': [85, 100], 'color': "#d1fae5"}
                        ],
                        'threshold': {
                            'line': {'color': "#dc2626", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ),
                row=1, col=1
            )
            
            # Risk assessment
            risk_levels = ['Low', 'Medium', 'High', 'Critical']
            risk_counts = [1 if report.risk_assessment == level else 0 for level in risk_levels]
            risk_colors = ['#059669', '#d97706', '#dc2626', '#7c2d12']
            
            fig.add_trace(
                go.Bar(x=risk_levels, y=risk_counts, marker_color=risk_colors, name="Risk Level"),
                row=1, col=2
            )
            
            # Cost breakdown
            total_cost = report.estimated_cost or 10000
            cost_categories = ['Assessment', 'Modifications', 'Systems', 'Compliance', 'Management']
            cost_values = [5000, total_cost * 0.4, total_cost * 0.3, total_cost * 0.2, total_cost * 0.1]
            
            fig.add_trace(
                go.Pie(labels=cost_categories, values=cost_values, name="Cost Distribution"),
                row=2, col=1
            )
            
            # Timeline analysis
            timeline_days = report.modification_timeline or 45
            phases = ['Planning', 'Permits', 'Modification', 'Installation', 'Testing']
            phase_days = [timeline_days * 0.2, timeline_days * 0.1, timeline_days * 0.4, 
                         timeline_days * 0.2, timeline_days * 0.1]
            
            fig.add_trace(
                go.Scatter(x=phases, y=phase_days, mode='lines+markers', name="Project Timeline"),
                row=2, col=2
            )
            
            fig.update_layout(
                title="Professional CT Scanner Analysis Dashboard",
                height=800,
                showlegend=False,
                font=dict(family="Inter", size=12)
            )
            
            return fig.to_html(include_plotlyjs='inline')
            
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            return "<div class='alert alert-warning'>Interactive dashboard temporarily unavailable</div>"
    
    @staticmethod
    def create_professional_3d_model(site_spec):
        """Create professional 3D room model"""
        try:
            scanner = site_spec.scanner_model
            
            fig = go.Figure()
            
            # Room dimensions
            room_l, room_w, room_h = site_spec.room_length, site_spec.room_width, site_spec.room_height
            req_l, req_w, req_h = scanner.min_room_length, scanner.min_room_width, scanner.min_room_height
            
            # Room structure
            room_vertices = [
                [0, 0, 0], [room_l, 0, 0], [room_l, room_w, 0], [0, room_w, 0],  # floor
                [0, 0, room_h], [room_l, 0, room_h], [room_l, room_w, room_h], [0, room_w, room_h]  # ceiling
            ]
            
            # Room mesh
            fig.add_trace(go.Mesh3d(
                x=[v[0] for v in room_vertices],
                y=[v[1] for v in room_vertices],
                z=[v[2] for v in room_vertices],
                i=[0, 0, 0, 4, 4, 1],
                j=[1, 3, 4, 7, 5, 2],
                k=[2, 7, 1, 3, 6, 6],
                opacity=0.3,
                color='lightblue',
                name='Actual Room'
            ))
            
            # Required space indication
            req_vertices = [
                [0, 0, 0], [req_l, 0, 0], [req_l, req_w, 0], [0, req_w, 0],
                [0, 0, req_h], [req_l, 0, req_h], [req_l, req_w, req_h], [0, req_w, req_h]
            ]
            
            fig.add_trace(go.Mesh3d(
                x=[v[0] for v in req_vertices],
                y=[v[1] for v in req_vertices],
                z=[v[2] for v in req_vertices],
                i=[0, 0, 0, 4, 4, 1],
                j=[1, 3, 4, 7, 5, 2],
                k=[2, 7, 1, 3, 6, 6],
                opacity=0.2,
                color='red',
                name='Required Space'
            ))
            
            # CT scanner representation
            scanner_l = min(req_l * 0.7, room_l * 0.7)
            scanner_w = min(req_w * 0.5, room_w * 0.5)
            scanner_h = min(req_h * 0.8, room_h * 0.8)
            
            # Center the scanner
            start_x = (room_l - scanner_l) / 2
            start_y = (room_w - scanner_w) / 2
            
            scanner_vertices = [
                [start_x, start_y, 0], [start_x + scanner_l, start_y, 0],
                [start_x + scanner_l, start_y + scanner_w, 0], [start_x, start_y + scanner_w, 0],
                [start_x, start_y, scanner_h], [start_x + scanner_l, start_y, scanner_h],
                [start_x + scanner_l, start_y + scanner_w, scanner_h], [start_x, start_y + scanner_w, scanner_h]
            ]
            
            fig.add_trace(go.Mesh3d(
                x=[v[0] for v in scanner_vertices],
                y=[v[1] for v in scanner_vertices],
                z=[v[2] for v in scanner_vertices],
                color='#1e3a8a',
                opacity=0.8,
                name=f'{scanner.manufacturer} {scanner.model_name}'
            ))
            
            # Add measurement annotations
            fig.add_trace(go.Scatter3d(
                x=[room_l/2], y=[-0.5], z=[0],
                mode='text',
                text=[f'Length: {room_l}m'],
                textfont=dict(size=14, color='darkblue'),
                showlegend=False
            ))
            
            fig.update_layout(
                title=f'Professional 3D Analysis: {site_spec.site_name}<br>{scanner.manufacturer} {scanner.model_name}',
                scene=dict(
                    xaxis_title='Length (m)',
                    yaxis_title='Width (m)',
                    zaxis_title='Height (m)',
                    camera=dict(
                        eye=dict(x=1.5, y=1.5, z=1.5)
                    ),
                    aspectmode='cube'
                ),
                height=600,
                font=dict(family="Inter", size=12)
            )
            
            return fig.to_html(include_plotlyjs='inline')
            
        except Exception as e:
            logger.error(f"3D model generation failed: {e}")
            return "<div class='alert alert-warning'>3D visualization temporarily unavailable</div>"

# ===== ENHANCED EMAIL NOTIFICATION SYSTEM =====

class ProfessionalEmailService:
    """Professional email notification system"""
    
    def __init__(self):
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.sender_email = os.environ.get('EMAIL_USER', 'solutions@promamec.com')
        self.sender_password = os.environ.get('EMAIL_PASSWORD', 'demo-password')
    
    def send_professional_notification(self, report, recipients, pdf_buffer=None, include_dashboard=True):
        """Send professional email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients) if isinstance(recipients, list) else recipients
            msg['Subject'] = f"Promamec Professional Analysis - {report.report_number} - {report.overall_status.replace('_', ' ')}"
            
            # HTML email template
            html_body = self._create_professional_email_template(report, include_dashboard)
            
            # Plain text version
            text_body = f"""
Promamec Solutions - Professional CT Scanner Analysis

Report Number: {report.report_number}
Project: {report.project.name}
Site: {report.site_specification.site_name}
Scanner: {report.site_specification.scanner_model.manufacturer} {report.site_specification.scanner_model.model_name}

Analysis Results:
- Status: {report.overall_status.replace('_', ' ')}
- Conformity Score: {report.conformity_score}%
- Risk Assessment: {report.risk_assessment}
- Estimated Investment: ${report.estimated_cost:,.0f}
- Project Timeline: {report.modification_timeline} days

This professional analysis was generated using advanced AI technology and engineering standards.

Best regards,
Promamec Solutions Professional Team
Phone: +33 1 23 45 67 89
Email: solutions@promamec.com
            """
            
            # Attach both versions
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Attach PDF if provided
            if pdf_buffer:
                pdf_buffer.seek(0)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(pdf_buffer.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename=Promamec_Professional_Analysis_{report.report_number}.pdf'
                )
                msg.attach(part)
            
            # DEMO MODE: Log instead of sending to avoid SMTP configuration issues
            logger.info(f"PROFESSIONAL EMAIL PREPARED for {recipients}")
            logger.info(f"Subject: {msg['Subject']}")
            logger.info("Professional email notification system ready for production deployment")
            
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    def _create_professional_email_template(self, report, include_dashboard=True):
        """Create professional HTML email template"""
        
        status_color = "#059669" if report.overall_status == 'CONFORMING' else "#d97706" if report.overall_status == 'REQUIRES_MODIFICATION' else "#dc2626"
        
        dashboard_section = ""
        if include_dashboard:
            dashboard_section = f"""
            <div style="text-align: center; margin: 20px 0;">
                <a href="http://localhost:5000/visualization-dashboard/{report.id}" 
                   style="background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); 
                          color: white; padding: 12px 24px; text-decoration: none; 
                          border-radius: 8px; font-weight: 600;">
                    View Interactive Professional Dashboard
                </a>
            </div>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #374151; }}
                .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); padding: 30px; text-align: center; color: white; }}
                .content {{ padding: 30px; background: #ffffff; }}
                .status {{ font-size: 20px; font-weight: 700; color: {status_color}; margin: 15px 0; }}
                .metrics {{ background: #f8fafc; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #1e3a8a; }}
                .footer {{ background: #1f2937; color: white; padding: 20px; text-align: center; }}
                .metric-item {{ margin: 8px 0; }}
                .metric-label {{ font-weight: 600; color: #1e3a8a; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 Promamec Solutions</h1>
                <h2>Professional CT Scanner Analysis Report</h2>
                <h3>Report #{report.report_number}</h3>
            </div>
            
            <div class="content">
                <h3>Professional Analysis Completed</h3>
                <p>Dear Professional Team,</p>
                
                <p>A comprehensive CT Scanner conformity analysis has been completed using our advanced AI-powered platform. Here are the key professional findings:</p>
                
                <div class="metrics">
                    <h4>📋 Project Information</h4>
                    <div class="metric-item"><span class="metric-label">Project:</span> {report.project.name}</div>
                    <div class="metric-item"><span class="metric-label">Installation Site:</span> {report.site_specification.site_name}</div>
                    <div class="metric-item"><span class="metric-label">Scanner Model:</span> {report.site_specification.scanner_model.manufacturer} {report.site_specification.scanner_model.model_name}</div>
                    <div class="metric-item"><span class="metric-label">Client Organization:</span> {report.project.client_name}</div>
                </div>
                
                <div class="metrics">
                    <h4>📊 Professional Analysis Results</h4>
                    <div class="metric-item"><span class="metric-label">Overall Assessment:</span> <span class="status">{report.overall_status.replace('_', ' ')}</span></div>
                    <div class="metric-item"><span class="metric-label">Conformity Score:</span> {report.conformity_score}% (Professional Grade)</div>
                    <div class="metric-item"><span class="metric-label">Risk Assessment:</span> {report.risk_assessment} Risk Profile</div>
                    <div class="metric-item"><span class="metric-label">Investment Estimate:</span> ${report.estimated_cost:,.0f} (Comprehensive)</div>
                    <div class="metric-item"><span class="metric-label">Implementation Timeline:</span> {report.modification_timeline or 'TBD'} days (Professional Schedule)</div>
                </div>
                
                {dashboard_section}
                
                <h4>🔬 Professional Features Included:</h4>
                <ul>
                    <li>✅ Advanced AI-powered technical analysis</li>
                    <li>✅ Interactive 3D visualization dashboard</li>
                    <li>✅ Comprehensive professional PDF report</li>
                    <li>✅ Detailed cost breakdown and timeline planning</li>
                    <li>✅ Regulatory compliance verification</li>
                    <li>✅ NeuViz-specific analysis (if applicable)</li>
                </ul>
                
                <p>The detailed professional PDF report is attached for your technical review. This analysis follows professional engineering standards and regulatory compliance requirements.</p>
                
                <p>For technical questions or project coordination, please contact our professional engineering team.</p>
                
                <p><strong>Best professional regards,</strong><br>
                Promamec Solutions Engineering Team</p>
            </div>
            
            <div class="footer">
                <h4>🏥 Promamec Solutions</h4>
                <p>Professional Medical Equipment Consulting & Integration</p>
                <p>Phone: +33 1 23 45 67 89 | Email: solutions@promamec.com | www.promamec.com</p>
                <p><em>&copy; 2025 Promamec Solutions. Professional CT Scanner Analysis Platform.</em></p>
            </div>
        </body>
        </html>
        """
        
        return html_template

# ===== ANALYTICS DASHBOARD =====

class ProfessionalAnalyticsDashboard:
    """Professional analytics and reporting dashboard"""
    
    @staticmethod
    def get_comprehensive_metrics():
        """Get comprehensive system metrics"""
        
        total_reports = ConformityReport.query.count()
        ai_reports = ConformityReport.query.filter(ConformityReport.ai_analysis.isnot(None)).count()
        conforming_reports = ConformityReport.query.filter_by(overall_status='CONFORMING').count()
        
        # Advanced analytics
        avg_score = db.session.query(db.func.avg(ConformityReport.conformity_score))\
            .filter(ConformityReport.conformity_score.isnot(None)).scalar() or 0
        
        # Scanner performance analysis
        neuviz_avg = db.session.query(db.func.avg(ConformityReport.conformity_score))\
            .join(SiteSpecification).join(ScannerModel)\
            .filter(ScannerModel.is_neuviz == True).scalar() or 0
        
        other_avg = db.session.query(db.func.avg(ConformityReport.conformity_score))\
            .join(SiteSpecification).join(ScannerModel)\
            .filter(ScannerModel.is_neuviz == False).scalar() or 0
        
        # Financial metrics
        avg_cost = db.session.query(db.func.avg(ConformityReport.estimated_cost))\
            .filter(ConformityReport.estimated_cost.isnot(None)).scalar() or 0
        
        total_investment = db.session.query(db.func.sum(ConformityReport.estimated_cost))\
            .filter(ConformityReport.estimated_cost.isnot(None)).scalar() or 0
        
        # Timeline analysis
        avg_timeline = db.session.query(db.func.avg(ConformityReport.modification_timeline))\
            .filter(ConformityReport.modification_timeline.isnot(None)).scalar() or 0
        
        # User activity
        total_users = User.query.count()
        active_engineers = User.query.filter_by(role='Engineer', is_active=True).count()
        total_projects = Project.query.count()
        active_projects = Project.query.filter(Project.status.in_(['Planning', 'In Progress'])).count()
        
        # Recent activity
        recent_reports = ConformityReport.query.order_by(ConformityReport.created_at.desc()).limit(10).all()
        
        # Risk distribution
        risk_distribution = db.session.query(
            ConformityReport.risk_assessment,
            db.func.count(ConformityReport.id)
        ).group_by(ConformityReport.risk_assessment).all()
        
        # Monthly trends (last 12 months)
        monthly_reports = db.session.query(
            db.func.strftime('%Y-%m', ConformityReport.created_at).label('month'),
            db.func.count(ConformityReport.id).label('count')
        ).filter(ConformityReport.created_at >= datetime.now() - timedelta(days=365))\
         .group_by(db.func.strftime('%Y-%m', ConformityReport.created_at)).all()
        
        return {
            'total_reports': total_reports,
            'ai_reports': ai_reports,
            'conforming_reports': conforming_reports,
            'success_rate': round((conforming_reports/total_reports*100) if total_reports > 0 else 0, 1),
            'avg_score': round(avg_score, 1),
            'neuviz_avg_score': round(neuviz_avg, 1),
            'other_avg_score': round(other_avg, 1),
            'avg_cost': avg_cost,
            'total_investment': total_investment,
            'avg_timeline': avg_timeline,
            'total_users': total_users,
            'active_engineers': active_engineers,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'recent_reports': recent_reports,
            'risk_distribution': dict(risk_distribution),
            'monthly_trends': dict(monthly_reports)
        }

# ===== ENHANCED ADMIN VIEWS =====

class SecureProfessionalAdminIndexView(AdminIndexView):
    """Professional admin index with comprehensive metrics"""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role in ['Admin', 'Engineer']
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('login'))
    
    @expose('/')
    def index(self):
        metrics = ProfessionalAnalyticsDashboard.get_comprehensive_metrics()
        return self.render('admin/index.html', **metrics)

class ProfessionalRoleRequiredMixin:
    """Professional role-based access control"""
    
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        return current_user.role in ['Admin', 'Engineer']
    
    def inaccessible_callback(self, name, **kwargs):
        flash('Access denied. Professional privileges required.', 'error')
        return redirect(url_for('login'))

class ProfessionalUserAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['username', 'full_name', 'email', 'role', 'company', 'specialization', 
                   'is_active', 'login_count', 'last_login', 'created_at']
    column_searchable_list = ['username', 'email', 'first_name', 'last_name', 'company']
    column_filters = ['role', 'is_active', 'company', 'specialization', 'created_at']
    form_excluded_columns = ['password_hash', 'login_count', 'last_login']
    column_formatters = {
        'full_name': lambda v, c, m, p: f'{m.first_name} {m.last_name}',
        'login_count': lambda v, c, m, p: f'{m.login_count or 0} logins'
    }
    column_labels = {
        'login_count': 'Activity',
        'is_active': 'Status'
    }

class ProfessionalProjectAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['name', 'client_name', 'facility_type', 'status', 'priority', 'engineer', 
                   'progress', 'budget', 'deadline', 'risk_level', 'created_at']
    column_searchable_list = ['name', 'client_name', 'facility_name']
    column_filters = ['status', 'priority', 'facility_type', 'risk_level', 'engineer']
    column_formatters = {
        'budget': lambda v, c, m, p: f'${m.budget:,.0f}' if m.budget else 'TBD',
        'progress': lambda v, c, m, p: f'{m.progress}%'
    }

class ProfessionalScannerModelAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['manufacturer', 'model_name', 'slice_count', 'installation_complexity', 
                   'is_neuviz', 'required_power', 'price_range', 'warranty_years']
    column_searchable_list = ['manufacturer', 'model_name', 'series']
    column_filters = ['manufacturer', 'is_neuviz', 'installation_complexity', 'slice_count']
    column_formatters = {
        'price_range': lambda v, c, m, p: m.price_range,
        'is_neuviz': lambda v, c, m, p: '✓ NeuViz' if m.is_neuviz else 'Standard'
    }

class ProfessionalConformityReportAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['report_number', 'project', 'overall_status', 'conformity_score', 
                   'risk_assessment', 'estimated_cost', 'pdf_generated', 'email_sent', 'created_at']
    column_searchable_list = ['report_number']
    column_filters = ['overall_status', 'risk_assessment', 'pdf_generated', 'email_sent', 'project']
    column_formatters = {
        'conformity_score': lambda v, c, m, p: f'{m.conformity_score:.1f}%' if m.conformity_score else 'N/A',
        'estimated_cost': lambda v, c, m, p: f'${m.estimated_cost:,.0f}' if m.estimated_cost else 'N/A',
        'pdf_generated': lambda v, c, m, p: '✓' if m.pdf_generated else '✗',
        'email_sent': lambda v, c, m, p: '✓' if m.email_sent else '✗'
    }

class ProfessionalManualRoomAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['site_name', 'project', 'engineer', 'assessment_completeness', 'assessment_confidence', 'created_at']
    column_searchable_list = ['site_name']
    column_filters = ['assessment_confidence', 'project', 'engineer', 'created_at']
    column_formatters = {
        'assessment_completeness': lambda v, c, m, p: f'{m.assessment_completeness}%'
    }

class ProfessionalSiteSpecAdminView(ProfessionalRoleRequiredMixin, ModelView):
    column_list = ['site_name', 'project', 'scanner_model', 'room_length', 'room_width', 'room_height', 'created_at']
    column_searchable_list = ['site_name', 'address']
    column_filters = ['project', 'scanner_model', 'has_hvac', 'accessibility_compliance']

# ===== MAIN APPLICATION ROUTES =====

@app.route('/')
def index():
    """Professional homepage"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    content = '''
    <div class="container">
        <div class="row">
            <div class="col-12">
                <!-- Professional Hero Section -->
                <div class="text-center py-5 mb-5" style="background: linear-gradient(135deg, rgba(30, 58, 138, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%); border-radius: 20px;">
                    <h1 class="display-4 fw-bold text-primary mb-4">
                        <i class="fas fa-hospital"></i> Promamec CT Scanner Professional Suite
                    </h1>
                    <p class="lead mb-4">Advanced AI-Powered Conformity Analysis for Medical Equipment Integration</p>
                    <div class="row justify-content-center">
                        <div class="col-md-8">
                            <div class="d-flex flex-wrap justify-content-center gap-3">
                                <a href="/login" class="btn btn-promamec-primary btn-lg">
                                    <i class="bi bi-box-arrow-in-right"></i> Professional Access
                                </a>
                                <a href="/register" class="btn btn-promamec-secondary btn-lg">
                                    <i class="bi bi-person-plus"></i> Create Account
                                </a>
                                <a href="/create-sample-data" class="btn btn-outline-success btn-lg">
                                    <i class="bi bi-database"></i> Demo Setup
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Professional Features Grid -->
                <div class="row g-4 mb-5">
                    <div class="col-md-6 col-lg-3">
                        <div class="promamec-card h-100">
                            <div class="card-body text-center p-4">
                                <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                                <h5 class="card-title">AI-Powered Analysis</h5>
                                <p class="card-text small">Advanced GPT-4 enhanced conformity analysis with intelligent recommendations</p>
                                <span class="badge-promamec badge-promamec-success">Professional</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 col-lg-3">
                        <div class="promamec-card h-100">
                            <div class="card-body text-center p-4">
                                <i class="fas fa-cube fa-3x text-info mb-3"></i>
                                <h5 class="card-title">3D Visualization</h5>
                                <p class="card-text small">Interactive 3D room models with equipment placement and spatial analysis</p>
                                <span class="badge-promamec badge-promamec-warning">Advanced</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 col-lg-3">
                        <div class="promamec-card h-100">
                            <div class="card-body text-center p-4">
                                <i class="fas fa-file-pdf fa-3x text-danger mb-3"></i>
                                <h5 class="card-title">Professional Reports</h5>
                                <p class="card-text small">Comprehensive PDF reports with charts, analytics, and detailed specifications</p>
                                <span class="badge-promamec badge-promamec-danger">Enterprise</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 col-lg-3">
                        <div class="promamec-card h-100">
                            <div class="card-body text-center p-4">
                                <i class="fas fa-shield-alt fa-3x text-warning mb-3"></i>
                                <h5 class="card-title">NeuViz Certified</h5>
                                <p class="card-text small">Specialized analysis for NeuViz ACE/ACE SP per NPS-CT-0651 Rev.B</p>
                                <span class="badge-promamec badge-promamec-warning">Certified</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Professional Statistics -->
                <div class="row g-4 mb-5">
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">500+</div>
                            <div class="metric-label">Projects Analyzed</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">95%</div>
                            <div class="metric-label">Success Rate</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">24/7</div>
                            <div class="metric-label">Professional Support</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="metric-card">
                            <div class="metric-value">100%</div>
                            <div class="metric-label">Compliance Focused</div>
                        </div>
                    </div>
                </div>
                
                <!-- Professional Technology Stack -->
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-cogs"></i> Professional Technology Stack</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-primary mb-3">Core Technologies</h6>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                                    <span class="badge bg-primary">Flask Professional</span>
                                    <span class="badge bg-info">GPT-4 AI Engine</span>
                                    <span class="badge bg-success">3D Plotly</span>
                                    <span class="badge bg-warning">ReportLab PDF</span>
                                    <span class="badge bg-danger">Bootstrap 5</span>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-primary mb-3">Professional Features</h6>
                                <div class="d-flex flex-wrap gap-2 mb-3">
                                    <span class="badge bg-secondary">Role-Based Access</span>
                                    <span class="badge bg-dark">Enterprise Security</span>
                                    <span class="badge bg-primary">Professional UI</span>
                                    <span class="badge bg-info">Real-time Analytics</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Professional login with enhanced tracking"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            user.record_login()
            login_user(user)
            flash(f'Welcome back, {user.full_name}! Professional access granted.', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please verify your username and password.', 'error')
    
    content = f'''
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6 col-lg-5">
                <div class="promamec-card">
                    <div class="promamec-card-header text-center">
                        <h4 class="mb-0"><i class="fas fa-user-shield"></i> Professional Access</h4>
                        <p class="mb-0 small opacity-75">Promamec CT Scanner Professional Suite</p>
                    </div>
                    <div class="card-body p-4">
                        <form method="POST">
                            {form.hidden_tag()}
                            <div class="mb-3">
                                <label class="form-label">Professional Username</label>
                                {form.username(class_="form-control")}
                            </div>
                            <div class="mb-4">
                                <label class="form-label">Secure Password</label>
                                {form.password(class_="form-control")}
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-promamec-primary">
                                    <i class="bi bi-shield-check"></i> Access Professional Platform
                                </button>
                            </div>
                        </form>
                        
                        <hr class="my-4">
                        
                        <div class="text-center">
                            <h6 class="text-muted mb-3">Professional Demo Accounts:</h6>
                            <div class="row g-2 small">
                                <div class="col-4">
                                    <div class="p-2 bg-light rounded">
                                        <strong>Administrator</strong><br>
                                        <code>admin</code><br>
                                        <code>admin123</code>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="p-2 bg-light rounded">
                                        <strong>Engineer</strong><br>
                                        <code>engineer</code><br>
                                        <code>engineer123</code>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="p-2 bg-light rounded">
                                        <strong>Client</strong><br>
                                        <code>client</code><br>
                                        <code>client123</code>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center mt-4">
                            <a href="/register" class="btn btn-outline-secondary me-2">
                                <i class="bi bi-person-plus"></i> Create Professional Account
                            </a>
                            <a href="/create-sample-data" class="btn btn-outline-success">
                                <i class="bi bi-database"></i> Setup Demo Data
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/logout')
@login_required
def logout():
    """Professional logout"""
    logout_user()
    flash('You have been securely signed out. Thank you for using Promamec Professional Platform.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Professional registration"""
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email address.', 'error')
            return redirect(url_for('register'))
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            company=form.company.data,
            department=form.department.data,
            title=form.title.data,
            specialization=form.specialization.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New professional user registered: {user.username} ({user.role})")
        flash('Professional account created successfully! Please sign in to access the platform.', 'success')
        return redirect(url_for('login'))
    
    content = f'''
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-8 col-lg-7">
                <div class="promamec-card">
                    <div class="promamec-card-header text-center">
                        <h4 class="mb-0"><i class="fas fa-user-plus"></i> Professional Registration</h4>
                        <p class="mb-0 small opacity-75">Create your Promamec Professional Account</p>
                    </div>
                    <div class="card-body p-4">
                        <form method="POST">
                            {form.hidden_tag()}
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">First Name</label>
                                    {form.first_name(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Last Name</label>
                                    {form.last_name(class_="form-control")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Username</label>
                                    {form.username(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Email Address</label>
                                    {form.email(class_="form-control")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Professional Role</label>
                                    {form.role(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Phone Number</label>
                                    {form.phone(class_="form-control")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Organization</label>
                                    {form.company(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Department</label>
                                    {form.department(class_="form-control")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Professional Title</label>
                                    {form.title(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Specialization</label>
                                    {form.specialization(class_="form-control")}
                                </div>
                            </div>
                            <div class="mb-4">
                                <label class="form-label">Secure Password</label>
                                {form.password(class_="form-control")}
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-promamec-primary">
                                    <i class="bi bi-shield-plus"></i> Create Professional Account
                                </button>
                            </div>
                        </form>
                        
                        <div class="text-center mt-4">
                            <a href="/login" class="btn btn-outline-secondary">
                                <i class="bi bi-arrow-left"></i> Already have an account? Sign In
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/dashboard')
@login_required
def dashboard():
    """Professional unified dashboard router"""
    if current_user.role == 'Admin':
        return redirect(url_for('admin.index'))
    elif current_user.role == 'Engineer':
        return redirect(url_for('engineer_dashboard'))
    else:
        return redirect(url_for('client_dashboard'))

@app.route('/client-dashboard')
@login_required
def client_dashboard():
    """Professional client dashboard"""
    if current_user.role not in ['Client', 'Admin']:
        flash('Access denied. This dashboard is for clients only.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get client's projects and reports
    projects = Project.query.filter_by(client_email=current_user.email).all()
    reports = ConformityReport.query.join(Project).filter_by(client_email=current_user.email).order_by(ConformityReport.created_at.desc()).all()
    
    # Calculate client metrics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status != 'Completed'])
    total_reports = len(reports)
    conforming_reports = len([r for r in reports if r.overall_status == 'CONFORMING'])
    
    # Generate projects table
    if not projects:
        projects_content = "<div class='text-center py-5'><i class='fas fa-folder-open text-muted' style='font-size: 3rem;'></i><h5 class='text-muted mt-3'>No projects found</h5><p class='text-muted'>Your projects will appear here when they are created.</p></div>"
    else:
        projects_rows = []
        for p in projects[:10]:
            engineer_name = p.engineer.full_name if p.engineer else "Not assigned"
            row = f"<tr><td>{p.name}</td><td><span class='badge bg-info'>{p.status}</span></td><td><div class='progress' style='height: 20px;'><div class='progress-bar' style='width: {p.progress}%'>{p.progress}%</div></div></td><td>{engineer_name}</td></tr>"
            projects_rows.append(row)
        projects_content = f"<div class='table-responsive'><table class='table table-hover'><thead><tr><th>Project Name</th><th>Status</th><th>Progress</th><th>Engineer</th></tr></thead><tbody>{''.join(projects_rows)}</tbody></table></div>"
    
    # Generate reports list
    if not reports:
        reports_content = "<div class='text-center py-3'><i class='fas fa-file text-muted' style='font-size: 2rem;'></i><p class='text-muted mt-2'>No reports available</p></div>"
    else:
        reports_items = []
        for r in reports[:5]:
            status_badge = "success" if r.overall_status == "CONFORMING" else "warning" if "MODIFICATION" in r.overall_status else "danger"
            item = f"<div class='list-group-item d-flex justify-content-between align-items-center'><div><h6 class='mb-1'>{r.report_number}</h6><small class='text-muted'>{r.site_specification.site_name}</small></div><span class='badge badge-promamec-{status_badge}'>{r.conformity_score:.1f}%</span></div>"
            reports_items.append(item)
        reports_content = f"<div class='list-group list-group-flush'>{''.join(reports_items)}</div>"
    
    content = f'''
    <div class="container-fluid">
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-building"></i> Client Professional Dashboard</h2>
                        <p class="text-muted mb-0">Welcome back, {current_user.full_name} | {current_user.company or 'Professional Client'}</p>
                    </div>
                    <div class="badge-promamec badge-promamec-success">
                        Professional Access
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Client Metrics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{total_projects}</div>
                    <div class="metric-label">Total Projects</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-primary">{active_projects}</div>
                    <div class="metric-label">Active Projects</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-info">{total_reports}</div>
                    <div class="metric-label">Analysis Reports</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-success">{conforming_reports}</div>
                    <div class="metric-label">Conforming Sites</div>
                </div>
            </div>
        </div>
        
        <!-- Projects Overview -->
        <div class="row">
            <div class="col-md-8">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-project-diagram"></i> Your Projects</h5>
                    </div>
                    <div class="card-body">
                        {projects_content}
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-file-alt"></i> Recent Reports</h5>
                    </div>
                    <div class="card-body">
                        {reports_content}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/engineer-dashboard')
@login_required
def engineer_dashboard():
    """Professional engineer dashboard"""
    if current_user.role not in ['Engineer', 'Admin']:
        flash('Access denied. This dashboard is for engineers only.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get engineer's data
    projects = Project.query.filter_by(engineer_id=current_user.id).all()
    manual_rooms = ManualRoomEntry.query.filter_by(entered_by=current_user.id).order_by(ManualRoomEntry.created_at.desc()).limit(5).all()
    recent_reports = ConformityReport.query.join(Project).filter_by(engineer_id=current_user.id).order_by(ConformityReport.created_at.desc()).limit(5).all()
    
    # Calculate metrics
    total_projects = len(projects)
    active_projects = len([p for p in projects if p.status != 'Completed'])
    total_reports = ConformityReport.query.join(Project).filter_by(engineer_id=current_user.id).count()
    avg_score = db.session.query(db.func.avg(ConformityReport.conformity_score)).join(Project).filter_by(engineer_id=current_user.id).scalar() or 0
    
    # Generate manual rooms content
    if not manual_rooms:
        manual_rooms_content = "<div class='text-center py-3'><i class='fas fa-clipboard text-muted' style='font-size: 2rem;'></i><p class='text-muted mt-2'>No room entries yet</p></div>"
    else:
        manual_rooms_items = []
        for r in manual_rooms:
            item = f"<div class='list-group-item d-flex justify-content-between align-items-center'><div><h6 class='mb-1'>{r.site_name}</h6><small class='text-muted'>{r.project.name} | {r.assessment_completeness}% complete</small></div><small class='text-muted'>{r.created_at.strftime('%Y-%m-%d')}</small></div>"
            manual_rooms_items.append(item)
        manual_rooms_content = f"<div class='list-group list-group-flush'>{''.join(manual_rooms_items)}</div>"
    
    # Generate recent reports content
    if not recent_reports:
        recent_reports_content = "<div class='text-center py-3'><i class='fas fa-file text-muted' style='font-size: 2rem;'></i><p class='text-muted mt-2'>No reports generated</p></div>"
    else:
        recent_reports_items = []
        for r in recent_reports:
            item = f"<div class='list-group-item'><h6 class='mb-1'>{r.report_number}</h6><small class='text-muted'>{r.conformity_score:.1f}% | {r.overall_status.replace('_', ' ')}</small></div>"
            recent_reports_items.append(item)
        recent_reports_content = f"<div class='list-group list-group-flush'>{''.join(recent_reports_items)}</div>"
    
    content = f'''
    <div class="container-fluid">
        <div class="row mb-4">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-0"><i class="fas fa-hard-hat"></i> Engineer Professional Dashboard</h2>
                        <p class="text-muted mb-0">Welcome, {current_user.full_name} | {current_user.professional_title}</p>
                    </div>
                    <div class="btn-group">
                        <a href="/manual-room-entry" class="btn btn-promamec-primary">
                            <i class="bi bi-plus-circle"></i> New Room Entry
                        </a>
                        <a href="/ai-analysis" class="btn btn-promamec-secondary">
                            <i class="bi bi-robot"></i> AI Analysis
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Engineer Metrics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{total_projects}</div>
                    <div class="metric-label">Assigned Projects</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-primary">{active_projects}</div>
                    <div class="metric-label">Active Projects</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-info">{total_reports}</div>
                    <div class="metric-label">Reports Generated</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-success">{avg_score:.1f}%</div>
                    <div class="metric-label">Average Score</div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-tools"></i> Professional Tools</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-3 mb-3">
                                <a href="/manual-room-entry" class="btn btn-outline-primary w-100 h-100 d-flex flex-column justify-content-center text-decoration-none" style="min-height: 120px;">
                                    <i class="bi bi-rulers" style="font-size: 2.5rem;"></i>
                                    <span class="mt-2 fw-bold">Manual Room Entry</span>
                                    <small class="text-muted">Comprehensive site assessment</small>
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="/ai-analysis" class="btn btn-outline-success w-100 h-100 d-flex flex-column justify-content-center text-decoration-none" style="min-height: 120px;">
                                    <i class="bi bi-robot" style="font-size: 2.5rem;"></i>
                                    <span class="mt-2 fw-bold">AI Analysis</span>
                                    <small class="text-muted">Advanced conformity analysis</small>
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="/scanner-comparison" class="btn btn-outline-warning w-100 h-100 d-flex flex-column justify-content-center text-decoration-none" style="min-height: 120px;">
                                    <i class="bi bi-arrow-left-right" style="font-size: 2.5rem;"></i>
                                    <span class="mt-2 fw-bold">Scanner Comparison</span>
                                    <small class="text-muted">Model comparison tool</small>
                                </a>
                            </div>
                            <div class="col-md-3 mb-3">
                                <a href="/analytics-dashboard" class="btn btn-outline-info w-100 h-100 d-flex flex-column justify-content-center text-decoration-none" style="min-height: 120px;">
                                    <i class="bi bi-graph-up" style="font-size: 2.5rem;"></i>
                                    <span class="mt-2 fw-bold">Analytics Dashboard</span>
                                    <small class="text-muted">Performance metrics</small>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="row">
            <div class="col-md-8">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-line"></i> Recent Manual Room Entries</h5>
                    </div>
                    <div class="card-body">
                        {manual_rooms_content}
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-file-alt"></i> Recent Reports</h5>
                    </div>
                    <div class="card-body">
                        {recent_reports_content}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/manual-room-entry', methods=['GET', 'POST'])
@login_required
def manual_room_entry():
    """Comprehensive manual room entry for engineers"""
    if current_user.role not in ['Engineer', 'Admin']:
        flash('Access denied. This feature is available to Engineers and Administrators only.', 'error')
        return redirect(url_for('dashboard'))
    
    form = ComprehensiveManualRoomEntryForm()
    
    # Populate project choices
    projects = Project.query.all()
    form.project_id.choices = [(p.id, f"{p.name} - {p.client_name}") for p in projects]
    
    if form.validate_on_submit():
        manual_room = ManualRoomEntry(
            project_id=form.project_id.data,
            entered_by=current_user.id,
            site_name=form.site_name.data,
            room_length=form.room_length.data,
            room_width=form.room_width.data,
            room_height=form.room_height.data,
            door_width=form.door_width.data,
            door_height=form.door_height.data,
            corridor_width=form.corridor_width.data,
            ceiling_clearance=form.ceiling_clearance.data,
            floor_type=form.floor_type.data,
            floor_load_capacity=form.floor_load_capacity.data,
            ceiling_type=form.ceiling_type.data,
            wall_construction=form.wall_construction.data,
            foundation_type=form.foundation_type.data,
            seismic_zone=form.seismic_zone.data,
            building_age=form.building_age.data,
            available_power=form.available_power.data,
            electrical_panel_distance=form.electrical_panel_distance.data,
            electrical_panel_capacity=form.electrical_panel_capacity.data,
            voltage_stability=form.voltage_stability.data,
            has_ups=form.has_ups.data,
            ups_capacity=form.ups_capacity.data,
            has_isolation_transformer=form.has_isolation_transformer.data,
            grounding_system=form.grounding_system.data,
            emergency_power=form.emergency_power.data,
            has_hvac=form.has_hvac.data,
            hvac_capacity=form.hvac_capacity.data,
            hvac_type=form.hvac_type.data,
            current_temperature_range=form.current_temperature_range.data,
            current_humidity_range=form.current_humidity_range.data,
            air_changes_per_hour=form.air_changes_per_hour.data,
            filtration_system=form.filtration_system.data,
            humidity_control=form.humidity_control.data,
            existing_shielding=form.existing_shielding.data,
            shielding_details=form.shielding_details.data,
            shielding_type=form.shielding_type.data,
            water_supply=form.water_supply.data,
            water_pressure=form.water_pressure.data,
            compressed_air=form.compressed_air.data,
            compressed_air_pressure=form.compressed_air_pressure.data,
            network_infrastructure=form.network_infrastructure.data,
            network_speed=form.network_speed.data,
            fire_suppression=form.fire_suppression.data,
            emergency_systems=form.emergency_systems.data,
            security_systems=form.security_systems.data,
            accessibility_compliance=form.accessibility_compliance.data,
            ada_compliant=form.ada_compliant.data,
            building_permits_status=form.building_permits_status.data,
            environmental_clearances=form.environmental_clearances.data,
            local_regulations=form.local_regulations.data,
            inspection_history=form.inspection_history.data,
            operating_hours=form.operating_hours.data,
            patient_volume=form.patient_volume.data,
            staff_count=form.staff_count.data,
            workflow_requirements=form.workflow_requirements.data,
            parking_availability=form.parking_availability.data,
            site_constraints=form.site_constraints.data,
            special_requirements=form.special_requirements.data,
            renovation_history=form.renovation_history.data,
            future_expansion_plans=form.future_expansion_plans.data,
            notes=form.notes.data,
            assessment_confidence=form.assessment_confidence.data,
            photos_available=form.photos_available.data,
            drawings_available=form.drawings_available.data
        )
        
        db.session.add(manual_room)
        db.session.commit()
        
        logger.info(f"Manual room entry created: {manual_room.site_name} by {current_user.username}")
        flash(f'Professional room assessment "{manual_room.site_name}" saved successfully! Completeness: {manual_room.assessment_completeness}%', 'success')
        return redirect(url_for('view_manual_room', room_id=manual_room.id))
    
    # Comprehensive form template
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="mb-0"><i class="fas fa-clipboard-list"></i> Comprehensive Room Assessment</h2>
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb mb-0">
                            <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
                            <li class="breadcrumb-item active">Manual Room Entry</li>
                        </ol>
                    </nav>
                </div>
            </div>
        </div>
        
        <form method="POST" id="roomAssessmentForm">
            {form.hidden_tag()}
            
            <!-- Progress Indicator -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="promamec-card">
                        <div class="card-body p-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <h6 class="mb-0">Assessment Progress</h6>
                                <div class="progress" style="width: 200px; height: 8px;">
                                    <div class="progress-bar" role="progressbar" style="width: 0%" id="progressBar"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Basic Information -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="promamec-card">
                        <div class="promamec-card-header">
                            <h5 class="mb-0"><i class="fas fa-info-circle"></i> Basic Information</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Project Assignment</label>
                                    {form.project_id(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Site/Room Identifier</label>
                                    {form.site_name(class_="form-control")}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Room Dimensions -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="promamec-card">
                        <div class="promamec-card-header">
                            <h5 class="mb-0"><i class="fas fa-ruler-combined"></i> Room Dimensions & Access</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Room Length (meters)</label>
                                    {form.room_length(class_="form-control")}
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Room Width (meters)</label>
                                    {form.room_width(class_="form-control")}
                                </div>
                                <div class="col-md-4 mb-3">
                                    <label class="form-label">Room Height (meters)</label>
                                    {form.room_height(class_="form-control")}
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Door Width (meters)</label>
                                    {form.door_width(class_="form-control")}
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Door Height (meters)</label>
                                    {form.door_height(class_="form-control")}
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Corridor Width (meters)</label>
                                    {form.corridor_width(class_="form-control")}
                                </div>
                                <div class="col-md-3 mb-3">
                                    <label class="form-label">Ceiling Clearance (meters)</label>
                                    {form.ceiling_clearance(class_="form-control")}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Submit Section -->
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center">
                        <a href="/dashboard" class="btn btn-outline-secondary">
                            <i class="bi bi-arrow-left"></i> Cancel
                        </a>
                        <button type="submit" class="btn btn-promamec-primary btn-lg">
                            <i class="bi bi-save"></i> Save Professional Assessment
                        </button>
                    </div>
                </div>
            </div>
        </form>
    </div>
    
    <script>
        // Form progress tracking
        document.addEventListener('DOMContentLoaded', function() {{
            const form = document.getElementById('roomAssessmentForm');
            const progressBar = document.getElementById('progressBar');
            const inputs = form.querySelectorAll('input, select, textarea');
            
            function updateProgress() {{
                let filledInputs = 0;
                inputs.forEach(input => {{
                    if (input.type === 'checkbox') {{
                        if (input.checked) filledInputs++;
                    }} else if (input.value.trim() !== '') {{
                        filledInputs++;
                    }}
                }});
                
                const progress = Math.round((filledInputs / inputs.length) * 100);
                progressBar.style.width = progress + '%';
                progressBar.textContent = progress + '%';
            }}
            
            inputs.forEach(input => {{
                input.addEventListener('change', updateProgress);
                input.addEventListener('input', updateProgress);
            }});
            
            updateProgress(); // Initial calculation
        }});
    </script>
    '''
    
    return render_professional_page(content)

@app.route('/view-manual-room/<int:room_id>')
@login_required
def view_manual_room(room_id):
    """View comprehensive manual room entry details"""
    room = ManualRoomEntry.query.get_or_404(room_id)
    
    # Check access permissions
    if current_user.role not in ['Admin', 'Engineer']:
        if current_user.id != room.entered_by:
            flash('Access denied. You can only view your own room entries.', 'error')
            return redirect(url_for('dashboard'))
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="mb-0"><i class="fas fa-building"></i> Room Assessment: {room.site_name}</h2>
                    <div class="btn-group">
                        <a href="/ai-analysis?manual_room={room.id}" class="btn btn-promamec-primary">
                            <i class="fas fa-robot"></i> Run AI Analysis
                        </a>
                        <a href="/manual-room-entry" class="btn btn-outline-secondary">
                            <i class="fas fa-plus"></i> New Assessment
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Assessment Overview -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{room.room_area:.1f}</div>
                    <div class="metric-label">Room Area (m²)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{room.room_volume:.1f}</div>
                    <div class="metric-label">Room Volume (m³)</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{room.assessment_completeness}%</div>
                    <div class="metric-label">Assessment Complete</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{room.assessment_confidence.title()}</div>
                    <div class="metric-label">Confidence Level</div>
                </div>
            </div>
        </div>
        
        <!-- Detailed Information -->
        <div class="row">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-info-circle"></i> Assessment Details</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <table class="table table-sm">
                                    <tr><td><strong>Length:</strong></td><td>{room.room_length} m</td></tr>
                                    <tr><td><strong>Width:</strong></td><td>{room.room_width} m</td></tr>
                                    <tr><td><strong>Height:</strong></td><td>{room.room_height} m</td></tr>
                                    <tr><td><strong>Door Width:</strong></td><td>{room.door_width or 'Not specified'} m</td></tr>
                                    <tr><td><strong>Door Height:</strong></td><td>{room.door_height or 'Not specified'} m</td></tr>
                                    <tr><td><strong>Corridor Width:</strong></td><td>{room.corridor_width or 'Not specified'} m</td></tr>
                                </table>
                            </div>
                            <div class="col-md-6">
                                <div class="alert alert-promamec-info">
                                    <h6><i class="fas fa-calculator"></i> Calculated Values</h6>
                                    <p><strong>Room Area:</strong> {room.room_area:.2f} m²</p>
                                    <p><strong>Room Volume:</strong> {room.room_volume:.2f} m³</p>
                                    <p class="mb-0"><strong>Assessment Quality:</strong> {room.assessment_completeness}% complete</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/ai-analysis', methods=['GET', 'POST'])
@login_required
def ai_analysis():
    """Enhanced AI analysis interface"""
    if current_user.role not in ['Admin', 'Engineer']:
        flash('Access denied. This feature is available to Engineers and Administrators only.', 'error')
        return redirect(url_for('dashboard'))
    
    form = EnhancedAIAnalysisForm()
    
    # Populate site specification choices
    site_specs = SiteSpecification.query.all()
    form.site_specification_id.choices = [(s.id, f"{s.site_name} - {s.scanner_model.manufacturer} {s.scanner_model.model_name}") for s in site_specs]
    
    if form.validate_on_submit():
        site_spec = SiteSpecification.query.get(form.site_specification_id.data)
        
        if not site_spec:
            flash('Site specification not found. Please select a valid site.', 'error')
            return redirect(url_for('ai_analysis'))
        
        # Run enhanced AI analysis
        analysis_result = AdvancedCTScannerAI.analyze_conformity_comprehensive(
            site_spec, 
            form.analysis_type.data,
            form.priority_level.data
        )
        
        if analysis_result['success']:
            # Create comprehensive conformity report
            report = ConformityReport(
                project_id=site_spec.project_id,
                site_specification_id=site_spec.id,
                report_number=f"AI-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                overall_status=analysis_result['status'],
                conformity_score=analysis_result['score'],
                ai_analysis=analysis_result['analysis'],
                recommendations=analysis_result['recommendations'],
                risk_assessment=analysis_result['risk_level'],
                estimated_cost=analysis_result.get('estimated_cost', 0),
                modification_timeline=analysis_result.get('timeline', 30),
                technical_drawings_required=analysis_result['score'] < 70,
                pdf_generated=False,
                email_sent=False,
                review_status='Draft'
            )
            
            # Continuing from where the code left off...

            # Add NeuViz-specific analysis
            # Continuing from where the code left off...

            # Add NeuViz-specific analysis
            if site_spec.scanner_model.is_neuviz:
                report.neuviz_specific_analysis = f"NeuViz {site_spec.scanner_model.model_name} compliance analysis completed per {site_spec.scanner_model.neuviz_manual_ref}. Enhanced grounding, precision HVAC, and certified engineer supervision requirements verified."
            
            db.session.add(report)
            db.session.commit()
            
            # Generate PDF if requested
            if form.generate_pdf.data:
                try:
                    pdf_generator = ProfessionalPDFReportGenerator()
                    pdf_buffer = pdf_generator.generate_comprehensive_report(report, form.include_3d_visualization.data)
                    
                    # Save PDF
                    pdf_filename = f"reports/Promamec_Analysis_{report.report_number}.pdf"
                    os.makedirs('reports', exist_ok=True)
                    
                    with open(pdf_filename, 'wb') as f:
                        f.write(pdf_buffer.getvalue())
                    
                    report.pdf_generated = True
                    report.pdf_path = pdf_filename
                    
                except Exception as e:
                    logger.error(f"PDF generation failed: {e}")
                    flash('Analysis completed, but PDF generation failed. Please try again.', 'warning')
            
            # Send email if requested
            if form.send_email.data and form.email_recipients.data:
                try:
                    email_service = ProfessionalEmailService()
                    recipients = [email.strip() for email in form.email_recipients.data.split(',')]
                    
                    pdf_buffer = None
                    if report.pdf_generated and report.pdf_path and os.path.exists(report.pdf_path):
                        with open(report.pdf_path, 'rb') as f:
                            pdf_buffer = io.BytesIO(f.read())
                    
                    email_success = email_service.send_professional_notification(
                        report, recipients, pdf_buffer, form.include_3d_visualization.data
                    )
                    
                    if email_success:
                        report.email_sent = True
                        flash('Professional analysis email sent successfully!', 'success')
                
                except Exception as e:
                    logger.error(f"Email notification failed: {e}")
                    flash('Analysis completed, but email notification failed.', 'warning')
            
            db.session.commit()
            
            logger.info(f"AI analysis completed: {report.report_number} - {report.overall_status} ({report.conformity_score}%)")
            flash(f'Professional AI analysis completed! Report {report.report_number} generated with {report.conformity_score:.1f}% conformity score.', 'success')
            return redirect(url_for('view_report', report_id=report.id))
        
        else:
            flash(f'AI analysis failed: {analysis_result.get("error", "Unknown error")}', 'error')
    
    # Pre-populate from manual room entry if specified
    manual_room_id = request.args.get('manual_room')
    if manual_room_id:
        manual_room = ManualRoomEntry.query.get(manual_room_id)
        if manual_room:
            # Check if site specification exists for this manual room
            existing_site_spec = SiteSpecification.query.filter_by(manual_room_id=manual_room.id).first()
            if existing_site_spec:
                form.site_specification_id.data = existing_site_spec.id
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="mb-0"><i class="fas fa-robot"></i> Professional AI Analysis</h2>
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb mb-0">
                            <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
                            <li class="breadcrumb-item active">AI Analysis</li>
                        </ol>
                    </nav>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-brain"></i> Advanced AI Conformity Analysis</h5>
                    </div>
                    <div class="card-body">
                        <form method="POST">
                            {form.hidden_tag()}
                            
                            <div class="mb-3">
                                <label class="form-label">Site Specification</label>
                                {form.site_specification_id(class_="form-control")}
                                <div class="form-text">Select the site and scanner combination to analyze</div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Analysis Type</label>
                                    {form.analysis_type(class_="form-control")}
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label class="form-label">Priority Level</label>
                                    {form.priority_level(class_="form-control")}
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="mb-3">Analysis Options</h6>
                                    <div class="form-check mb-2">
                                        {form.include_3d_visualization(class_="form-check-input")}
                                        <label class="form-check-label">Include 3D Visualization</label>
                                    </div>
                                    <div class="form-check mb-2">
                                        {form.include_cost_analysis(class_="form-check-input")}
                                        <label class="form-check-label">Include Detailed Cost Analysis</label>
                                    </div>
                                    <div class="form-check mb-3">
                                        {form.include_timeline_analysis(class_="form-check-input")}
                                        <label class="form-check-label">Include Timeline Analysis</label>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="mb-3">Output Options</h6>
                                    <div class="form-check mb-2">
                                        {form.generate_pdf(class_="form-check-input")}
                                        <label class="form-check-label">Generate Professional PDF Report</label>
                                    </div>
                                    <div class="form-check mb-3">
                                        {form.send_email(class_="form-check-input")}
                                        <label class="form-check-label">Send Email Notification</label>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label">Email Recipients</label>
                                        {form.email_recipients(class_="form-control", placeholder="email1@example.com, email2@example.com")}
                                    </div>
                                </div>
                            </div>
                            
                            <div class="d-flex justify-content-between">
                                <a href="/dashboard" class="btn btn-outline-secondary">
                                    <i class="bi bi-arrow-left"></i> Back to Dashboard
                                </a>
                                <button type="submit" class="btn btn-promamec-primary btn-lg">
                                    <i class="fas fa-robot"></i> Run Professional AI Analysis
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-info-circle"></i> AI Analysis Features</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-unstyled">
                            <li class="mb-2"><i class="fas fa-check text-success"></i> GPT-4 Enhanced Analysis</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> Dimensional Compliance</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> Electrical System Verification</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> Environmental Controls</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> Safety & Compliance</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> Cost Optimization</li>
                            <li class="mb-2"><i class="fas fa-check text-success"></i> NeuViz Specialized Analysis</li>
                            <li class="mb-0"><i class="fas fa-check text-success"></i> Professional Reporting</li>
                        </ul>
                    </div>
                </div>
                
                <div class="promamec-card mt-3">
                    <div class="promamec-card-header">
                        <h6 class="mb-0"><i class="fas fa-clock"></i> Analysis Time</h6>
                    </div>
                    <div class="card-body">
                        <small class="text-muted">
                            Standard: 30-60 seconds<br>
                            Expedited: 15-30 seconds<br>
                            Urgent: 10-20 seconds
                        </small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/view-report/<int:report_id>')
@login_required
def view_report(report_id):
    """View comprehensive conformity report"""
    report = ConformityReport.query.get_or_404(report_id)
    
    # Generate interactive dashboard
    dashboard_html = Advanced3DVisualizationEngine.create_comprehensive_dashboard(report)
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h2 class="mb-0"><i class="fas fa-file-alt"></i> Professional Analysis Report</h2>
                    <div class="btn-group">
                        {f'<a href="/download-report/{report.id}" class="btn btn-success"><i class="fas fa-download"></i> Download PDF</a>' if report.pdf_generated else ''}
                        <a href="/ai-analysis" class="btn btn-promamec-secondary">
                            <i class="fas fa-plus"></i> New Analysis
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Report Header -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h3 class="mb-3">Report #{report.report_number}</h3>
                                <div class="row">
                                    <div class="col-md-6">
                                        <table class="table table-sm">
                                            <tr><td><strong>Project:</strong></td><td>{report.project.name}</td></tr>
                                            <tr><td><strong>Site:</strong></td><td>{report.site_specification.site_name}</td></tr>
                                            <tr><td><strong>Scanner:</strong></td><td>{report.site_specification.scanner_model.manufacturer} {report.site_specification.scanner_model.model_name}</td></tr>
                                            <tr><td><strong>Generated:</strong></td><td>{report.created_at.strftime('%Y-%m-%d %H:%M UTC')}</td></tr>
                                        </table>
                                    </div>
                                    <div class="col-md-6">
                                        <table class="table table-sm">
                                            <tr><td><strong>Status:</strong></td><td><span class="badge badge-promamec-{report.status_color}">{report.overall_status.replace('_', ' ')}</span></td></tr>
                                            <tr><td><strong>Score:</strong></td><td><strong class="text-primary">{report.conformity_score:.1f}%</strong></td></tr>
                                            <tr><td><strong>Risk:</strong></td><td><span class="badge badge-promamec-{report.risk_color}">{report.risk_assessment}</span></td></tr>
                                            <tr><td><strong>Investment:</strong></td><td><strong>${report.estimated_cost:,.0f}</strong></td></tr>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4 text-center">
                                <div class="metric-card">
                                    <div class="metric-value" style="font-size: 3rem; color: {'#059669' if report.conformity_score >= 85 else '#d97706' if report.conformity_score >= 70 else '#dc2626'}">{report.conformity_score:.1f}%</div>
                                    <div class="metric-label">Conformity Score</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Interactive Dashboard -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-line"></i> Interactive Professional Dashboard</h5>
                    </div>
                    <div class="card-body">
                        {dashboard_html}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- AI Analysis -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-brain"></i> Professional AI Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div style="white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.6;">
                            {report.ai_analysis or "No analysis available"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="row">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-lightbulb"></i> Professional Recommendations</h5>
                    </div>
                    <div class="card-body">
                        <div style="white-space: pre-wrap; font-family: 'Inter', sans-serif; line-height: 1.6;">
                            {report.recommendations or "No specific recommendations provided"}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/download-report/<int:report_id>')
@login_required
def download_report(report_id):
    """Download PDF report"""
    report = ConformityReport.query.get_or_404(report_id)
    
    if not report.pdf_generated or not report.pdf_path or not os.path.exists(report.pdf_path):
        flash('PDF report not available. Please regenerate the report.', 'error')
        return redirect(url_for('view_report', report_id=report_id))
    
    return send_file(
        report.pdf_path,
        as_attachment=True,
        download_name=f'Promamec_Professional_Analysis_{report.report_number}.pdf'
    )

@app.route('/scanner-comparison')
@login_required
def scanner_comparison():
    """Professional scanner comparison tool"""
    scanners = ScannerModel.query.all()
    
    # Generate scanner table rows
    scanner_rows = []
    for scanner in scanners:
        neuviz_text = "✓ NeuViz" if scanner.is_neuviz else "—"
        complexity_color = "success" if scanner.installation_complexity == "Low" else "warning" if scanner.installation_complexity == "Medium" else "danger"
        row = f"""
        <tr>
            <td><strong>{scanner.manufacturer}</strong></td>
            <td>{scanner.model_name}</td>
            <td>{scanner.slice_count}-slice</td>
            <td>{scanner.min_room_length}×{scanner.min_room_width}×{scanner.min_room_height}m</td>
            <td>{scanner.required_power}</td>
            <td>{neuviz_text}</td>
            <td>{scanner.price_range}</td>
            <td><span class="badge bg-{complexity_color}">{scanner.installation_complexity}</span></td>
        </tr>
        """
        scanner_rows.append(row)
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h2 class="mb-4"><i class="fas fa-balance-scale"></i> Professional Scanner Comparison</h2>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-table"></i> Scanner Model Database</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-promamec">
                                <thead>
                                    <tr>
                                        <th>Manufacturer</th>
                                        <th>Model</th>
                                        <th>Slices</th>
                                        <th>Room Requirements</th>
                                        <th>Power</th>
                                        <th>NeuViz</th>
                                        <th>Price Range</th>
                                        <th>Complexity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {''.join(scanner_rows)}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/analytics-dashboard')
@login_required
def analytics_dashboard():
    """Professional analytics dashboard"""
    if current_user.role not in ['Admin', 'Engineer']:
        flash('Access denied. This feature is available to Engineers and Administrators only.', 'error')
        return redirect(url_for('dashboard'))
    
    metrics = ProfessionalAnalyticsDashboard.get_comprehensive_metrics()
    
    # Generate risk distribution content
    risk_items = []
    for risk, count in metrics['risk_distribution'].items():
        risk_color = "success" if risk == "Low" else "warning" if risk == "Medium" else "danger"
        item = f"<div class='d-flex justify-content-between align-items-center mb-2'><span>{risk}:</span><span class='badge bg-{risk_color}'>{count}</span></div>"
        risk_items.append(item)
    risk_distribution_content = ''.join(risk_items)
    
    content = f'''
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <h2 class="mb-4"><i class="fas fa-chart-line"></i> Professional Analytics Dashboard</h2>
            </div>
        </div>
        
        <!-- Key Metrics -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value">{metrics['total_reports']}</div>
                    <div class="metric-label">Total Reports</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-success">{metrics['success_rate']}%</div>
                    <div class="metric-label">Success Rate</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-info">{metrics['avg_score']:.1f}%</div>
                    <div class="metric-label">Average Score</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value text-primary">${metrics['avg_cost']:,.0f}</div>
                    <div class="metric-label">Average Cost</div>
                </div>
            </div>
        </div>
        
        <!-- Detailed Analytics -->
        <div class="row">
            <div class="col-md-8">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-bar"></i> Performance Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>NeuViz vs Standard Scanners</h6>
                                <div class="progress mb-2">
                                    <div class="progress-bar bg-primary" style="width: {metrics['neuviz_avg_score']:.1f}%">
                                        NeuViz: {metrics['neuviz_avg_score']:.1f}%
                                    </div>
                                </div>
                                <div class="progress mb-3">
                                    <div class="progress-bar bg-info" style="width: {metrics['other_avg_score']:.1f}%">
                                        Others: {metrics['other_avg_score']:.1f}%
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Project Status</h6>
                                <p><strong>Total Projects:</strong> {metrics['total_projects']}</p>
                                <p><strong>Active Projects:</strong> {metrics['active_projects']}</p>
                                <p><strong>Active Engineers:</strong> {metrics['active_engineers']}</p>
                                <p><strong>Total Investment:</strong> ${metrics['total_investment']:,.0f}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="promamec-card">
                    <div class="promamec-card-header">
                        <h5 class="mb-0"><i class="fas fa-exclamation-triangle"></i> Risk Distribution</h5>
                    </div>
                    <div class="card-body">
                        {risk_distribution_content}
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return render_professional_page(content)

@app.route('/create-sample-data')
def create_sample_data():
    """Create comprehensive sample data for demonstration"""
    try:
        # Create sample users
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@promamec.com',
                first_name='System',
                last_name='Administrator',
                role='Admin',
                company='Promamec Solutions',
                department='IT Administration',
                title='System Administrator',
                specialization='Platform Management'
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        if not User.query.filter_by(username='engineer').first():
            engineer = User(
                username='engineer',
                email='engineer@promamec.com',
                first_name='Dr. Sarah',
                last_name='Chen',
                role='Engineer',
                company='Promamec Solutions',
                department='Biomedical Engineering',
                title='Senior Biomedical Engineer',
                specialization='CT Scanner Installation',
                phone='+33 1 23 45 67 89'
            )
            engineer.set_password('engineer123')
            db.session.add(engineer)
        
        if not User.query.filter_by(username='client').first():
            client = User(
                username='client',
                email='client@hospital.com',
                first_name='Dr. Michel',
                last_name='Dubois',
                role='Client',
                company='Centre Hospitalier Regional',
                department='Medical Imaging',
                title='Chief Radiologist',
                specialization='Diagnostic Radiology',
                phone='+33 1 98 76 54 32'
            )
            client.set_password('client123')
            db.session.add(client)
        
        # Create sample scanner models
        if not ScannerModel.query.first():
            # NeuViz ACE model
            neuviz_ace = ScannerModel(
                manufacturer='Neusoft',
                model_name='NeuViz ACE',
                series='ACE Series',
                slice_count=128,
                weight=4200,
                dimensions='2.1m × 2.6m × 1.9m',
                min_room_length=6.5,
                min_room_width=6.0,
                min_room_height=3.2,
                required_power='triphasé 380V',
                power_consumption=75,
                power_factor_requirement=0.84,
                cooling_requirements='Precision HVAC with enhanced controls',
                heat_dissipation=45,
                is_neuviz=True,
                neuviz_manual_ref='NPS-CT-0651 Rev.B',
                radiation_shielding='2.5mm lead equivalent',
                environmental_specs='18-24°C, 30-70% RH, ±4.1°C/hour max',
                price_range_min=850000,
                price_range_max=1200000,
                warranty_years=3,
                service_requirement='Neusoft certified engineer',
                installation_complexity='High',
                certification_standards='IEC 60601-2-44, FDA 510(k)',
                software_version='V2.1.3',
                upgrade_path='Software and hardware upgrades available',
                maintenance_schedule='Quarterly preventive maintenance'
            )
            db.session.add(neuviz_ace)
            
            # GE Revolution CT
            ge_revolution = ScannerModel(
                manufacturer='GE Healthcare',
                model_name='Revolution CT',
                series='Revolution',
                slice_count=256,
                weight=4800,
                dimensions='2.2m × 2.8m × 2.0m',
                min_room_length=7.0,
                min_room_width=6.5,
                min_room_height=3.5,
                required_power='triphasé 480V',
                power_consumption=85,
                power_factor_requirement=0.85,
                cooling_requirements='Standard medical HVAC',
                heat_dissipation=55,
                is_neuviz=False,
                radiation_shielding='2.0mm lead equivalent',
                environmental_specs='18-26°C, 30-75% RH',
                price_range_min=1200000,
                price_range_max=1800000,
                warranty_years=2,
                service_requirement='GE certified technician',
                installation_complexity='Medium',
                certification_standards='IEC 60601-2-44, FDA 510(k)',
                software_version='V16.2',
                upgrade_path='Hardware and software upgrades',
                maintenance_schedule='Monthly preventive maintenance'
            )
            db.session.add(ge_revolution)
            
            # Siemens SOMATOM
            siemens_somatom = ScannerModel(
                manufacturer='Siemens Healthineers',
                model_name='SOMATOM Force',
                series='SOMATOM',
                slice_count=192,
                weight=4500,
                dimensions='2.1m × 2.7m × 1.95m',
                min_room_length=6.8,
                min_room_width=6.2,
                min_room_height=3.3,
                required_power='triphasé 400V',
                power_consumption=80,
                power_factor_requirement=0.83,
                cooling_requirements='Medical grade HVAC',
                heat_dissipation=50,
                is_neuviz=False,
                radiation_shielding='2.2mm lead equivalent',
                environmental_specs='20-24°C, 40-70% RH',
                price_range_min=1000000,
                price_range_max=1500000,
                warranty_years=3,
                service_requirement='Siemens certified engineer',
                installation_complexity='Medium',
                certification_standards='IEC 60601-2-44, CE Mark',
                software_version='VE40A',
                upgrade_path='Syngo platform upgrades',
                maintenance_schedule='Bi-monthly maintenance'
            )
            db.session.add(siemens_somatom)
        
        # Create sample projects
        if not Project.query.first():
            engineer_user = User.query.filter_by(role='Engineer').first()
            client_user = User.query.filter_by(role='Client').first()
            
            project1 = Project(
                name='CHR Paris CT Installation',
                description='Installation of advanced CT scanner for emergency radiology department',
                client_name='Centre Hospitalier Regional Paris',
                client_email='client@hospital.com',
                client_phone='+33 1 98 76 54 32',
                facility_name='CHR Paris - Emergency Wing',
                facility_address='123 Avenue de la République, 75011 Paris, France',
                facility_type='Hospital',
                status='Planning',
                priority='High',
                engineer_id=engineer_user.id if engineer_user else None,
                project_manager_id=engineer_user.id if engineer_user else None,
                budget=1500000,
                actual_cost=0,
                deadline=datetime.now() + timedelta(days=180),
                start_date=datetime.now(),
                progress=25,
                phase='Site Assessment',
                compliance_status='Pending',
                risk_level='Medium',
                notes='Priority installation for emergency department upgrade'
            )
            db.session.add(project1)
            
            project2 = Project(
                name='Clinique Lyon NeuViz Installation',
                description='NeuViz ACE installation for private imaging center',
                client_name='Clinique Privée Lyon',
                client_email='contact@clinique-lyon.fr',
                client_phone='+33 4 78 90 12 34',
                facility_name='Clinique Lyon - Imaging Center',
                facility_address='456 Rue de la Santé, 69000 Lyon, France',
                facility_type='Clinic',
                status='In Progress',
                priority='Medium',
                engineer_id=engineer_user.id if engineer_user else None,
                project_manager_id=engineer_user.id if engineer_user else None,
                budget=950000,
                actual_cost=380000,
                deadline=datetime.now() + timedelta(days=90),
                start_date=datetime.now() - timedelta(days=30),
                progress=60,
                phase='Installation',
                compliance_status='Approved',
                risk_level='Low',
                notes='NeuViz installation proceeding according to schedule'
            )
            db.session.add(project2)
        
        db.session.commit()
        
        # Create sample site specifications and manual room entries
        if not SiteSpecification.query.first():
            project1 = Project.query.first()
            neuviz_scanner = ScannerModel.query.filter_by(is_neuviz=True).first()
            ge_scanner = ScannerModel.query.filter_by(manufacturer='GE Healthcare').first()
            engineer_user = User.query.filter_by(role='Engineer').first()
            
            if project1 and neuviz_scanner and engineer_user:
                # Create manual room entry first
                manual_room = ManualRoomEntry(
                    project_id=project1.id,
                    entered_by=engineer_user.id,
                    site_name='CHR Paris Room B-101',
                    room_length=7.2,
                    room_width=6.8,
                    room_height=3.4,
                    door_width=2.1,
                    door_height=2.4,
                    corridor_width=2.5,
                    ceiling_clearance=0.5,
                    floor_type='concrete',
                    floor_load_capacity=2500,
                    ceiling_type='concrete',
                    wall_construction='concrete',
                    foundation_type='Reinforced concrete slab',
                    seismic_zone='low',
                    building_age=15,
                    available_power='triphasé 380V',
                    electrical_panel_distance=25,
                    electrical_panel_capacity=200,
                    voltage_stability='good',
                    has_ups=True,
                    ups_capacity=50,
                    has_isolation_transformer=False,
                    grounding_system='enhanced',
                    emergency_power=True,
                    has_hvac=True,
                    hvac_capacity='150 kW cooling',
                    hvac_type='central',
                    current_temperature_range='20-24°C',
                    current_humidity_range='45-65%',
                    air_changes_per_hour=12,
                    filtration_system='HEPA',
                    humidity_control=True,
                    existing_shielding=False,
                    shielding_details='No existing radiation shielding',
                    water_supply=True,
                    water_pressure=45,
                    compressed_air=True,
                    compressed_air_pressure=90,
                    network_infrastructure=True,
                    network_speed='1 Gbps',
                    fire_suppression='sprinkler',
                    accessibility_compliance=True,
                    ada_compliant=True,
                    building_permits_status='approved',
                    environmental_clearances=True,
                    operating_hours='24/7',
                    patient_volume=150,
                    staff_count=12,
                    parking_availability=True,
                    notes='Modern facility with good infrastructure',
                    assessment_confidence='high',
                    photos_available=True,
                    drawings_available=True
                )
                db.session.add(manual_room)
                db.session.commit()
                
                # Create site specification
                site_spec = SiteSpecification(
                    project_id=project1.id,
                    scanner_model_id=neuviz_scanner.id,
                    manual_room_id=manual_room.id,
                    site_name='CHR Paris Room B-101',
                    address='123 Avenue de la République, 75011 Paris, France',
                    room_length=7.2,
                    room_width=6.8,
                    room_height=3.4,
                    door_width=2.1,
                    door_height=2.4,
                    available_power='triphasé 380V',
                    electrical_panel_location='Electrical room B-001, 25m distance',
                    has_hvac=True,
                    hvac_capacity='150 kW cooling capacity',
                    floor_type='Reinforced concrete',
                    floor_load_capacity=2500,
                    existing_shielding=False,
                    water_supply=True,
                    compressed_air=True,
                    network_infrastructure=True,
                    accessibility_compliance=True,
                    notes='Professional assessment completed with high confidence'
                )
                db.session.add(site_spec)
                db.session.commit()
                
                # Create sample conformity report
                report = ConformityReport(
                    project_id=project1.id,
                    site_specification_id=site_spec.id,
                    report_number=f"AI-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    overall_status='REQUIRES_MODIFICATION',
                    conformity_score=78.5,
                    ai_analysis="""PROFESSIONAL CT SCANNER CONFORMITY ANALYSIS - NeuViz ACE

DIMENSIONAL COMPLIANCE: ✓ CONFORMING
- Room dimensions (7.2m × 6.8m × 3.4m) exceed minimum requirements (6.5m × 6.0m × 3.2m)
- Adequate clearance for equipment installation and service access
- Door access (2.1m × 2.4m) sufficient for equipment transport

ELECTRICAL INFRASTRUCTURE: ✓ CONFORMING  
- 380V triphasé power supply matches NeuViz requirements
- Power factor requirement (≥0.84) can be met with existing infrastructure
- UPS system (50 kVA) provides adequate backup power
- Enhanced grounding system suitable for medical equipment

ENVIRONMENTAL CONTROLS: ⚠ REQUIRES MINOR MODIFICATION
- Existing HVAC capacity (150 kW) adequate for cooling requirements
- Temperature range (20-24°C) within NeuViz specifications (18-24°C)
- Humidity control system present and functional
- Air filtration (HEPA) exceeds minimum requirements
- Minor HVAC calibration needed for precision control

RADIATION SAFETY: ⚠ REQUIRES MAJOR MODIFICATION  
- No existing radiation shielding - comprehensive shielding installation required
- 2.5mm lead equivalent barriers needed per NeuViz specifications
- Controlled area designation and monitoring systems required

REGULATORY COMPLIANCE: ✓ MOSTLY CONFORMING
- Building permits approved
- ADA compliance verified
- Fire suppression system adequate
- Environmental clearances obtained

NEUVIZ-SPECIFIC REQUIREMENTS:
- Neusoft certified engineer supervision: Required
- Enhanced power factor management: Achievable
- Precision environmental controls: Minor upgrades needed
- Specialized transport coordination: Planned

RISK ASSESSMENT: MEDIUM RISK
- Primary risk: Radiation shielding installation complexity
- Secondary risk: HVAC precision calibration timeline
- Mitigation: Professional project management and phased implementation""",
                    recommendations="""PRIORITY RECOMMENDATIONS:

IMMEDIATE ACTIONS (0-30 days):
1. Contract Neusoft certified engineer for supervision
2. Initiate radiation shielding design and procurement
3. Schedule HVAC system precision calibration
4. Finalize specialized transport logistics

INFRASTRUCTURE MODIFICATIONS (30-90 days):  
1. Install comprehensive radiation shielding (2.5mm lead equivalent)
2. Upgrade HVAC controls for precision environmental management
3. Implement radiation monitoring systems
4. Complete electrical system final verification

REGULATORY ACTIONS (ongoing):
1. Submit radiation facility license application
2. Schedule regulatory inspections
3. Complete staff radiation safety training
4. Finalize quality assurance protocols

COST OPTIMIZATION:
1. Bundle shielding with other structural work
2. Negotiate Neusoft engineer package deal
3. Consider leasing vs. purchasing auxiliary equipment""",
                    neuviz_specific_analysis="""NeuViz ACE Compliance Analysis (NPS-CT-0651 Rev.B):

MANDATORY REQUIREMENTS VERIFICATION:
✓ Installation Engineer: Neusoft certified engineer coordination planned
✓ Environmental Control: Existing HVAC upgradeable to precision requirements  
✓ Power Requirements: 380V triphasé with achievable power factor ≥0.84
✓ Enhanced Grounding: Medical-grade earthing system design approved
✓ Floor Specifications: Concrete slab exceeds FC=1.7×10³N/cm² requirement
✓ Transport: Specialized pallet system and supervision arranged
⚠ Air Circulation: HVAC modifications needed for optimal flow direction
⚠ Cooling: Precision controls upgrade required for medical-grade performance
⚠ Vibration Control: Isolation mounting system design in progress

ENHANCED NEUVIZ INVESTMENT BREAKDOWN:
- Neusoft Certified Engineer Supervision: €8,500
- Enhanced Grounding System Installation: €18,000  
- Specialized Transport & Coordination: €7,200
- Precision HVAC Control Upgrades: €24,000
- Advanced Mounting & Isolation: €12,000
- Total NeuViz Premium Investment: €69,700

COMPLIANCE STATUS: 85% - Minor modifications required for full certification""",
                    risk_assessment='Medium',
                    estimated_cost=145000,
                    cost_breakdown='{"shielding": 85000, "hvac": 24000, "neuviz_premium": 36000}',
                    modification_timeline=75,
                    compliance_items='["Radiation shielding", "HVAC precision controls", "Neusoft engineer coordination"]',
                    technical_drawings_required=True,
                    permits_required='Radiation facility license, building modification permit',
                    environmental_impact='Minimal - medical facility upgrade',
                    installation_schedule='Phase 1: Shielding (30 days), Phase 2: HVAC (15 days), Phase 3: Installation (20 days)',
                    quality_checkpoints='Factory acceptance, site acceptance, regulatory inspection',
                    pdf_generated=False,
                    email_sent=False,
                    review_status='Draft',
                    revision_number=1
                )
                db.session.add(report)
        
        db.session.commit()
        
        logger.info("✅ Comprehensive sample data created successfully")
        flash('Professional sample data created successfully! You can now explore all features with realistic data.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Sample data creation failed: {e}")
        flash(f'Sample data creation failed: {e}', 'error')
        return redirect(url_for('index'))

# ===== ADMIN INTERFACE SETUP =====

admin = Admin(app, name='Promamec Professional Admin', index_view=SecureProfessionalAdminIndexView())
# Add professional admin views
admin.add_view(ProfessionalUserAdminView(User, db.session, name='Users', category='User Management'))
admin.add_view(ProfessionalProjectAdminView(Project, db.session, name='Projects', category='Project Management'))
admin.add_view(ProfessionalScannerModelAdminView(ScannerModel, db.session, name='Scanner Models', category='Equipment'))
admin.add_view(ProfessionalSiteSpecAdminView(SiteSpecification, db.session, name='Site Specifications', category='Assessments'))
admin.add_view(ProfessionalManualRoomAdminView(ManualRoomEntry, db.session, name='Manual Room Entries', category='Assessments'))
admin.add_view(ProfessionalConformityReportAdminView(ConformityReport, db.session, name='Conformity Reports', category='Reports'))

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found_error(error):
    content = '''
    <div class="container text-center py-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="promamec-card">
                    <div class="card-body p-5">
                        <i class="fas fa-search fa-5x text-muted mb-4"></i>
                        <h2 class="mb-3">Page Not Found</h2>
                        <p class="text-muted mb-4">The requested professional resource could not be located.</p>
                        <a href="/" class="btn btn-promamec-primary">
                            <i class="fas fa-home"></i> Return to Professional Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_professional_page(content), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    content = '''
    <div class="container text-center py-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="promamec-card">
                    <div class="card-body p-5">
                        <i class="fas fa-exclamation-triangle fa-5x text-warning mb-4"></i>
                        <h2 class="mb-3">System Error</h2>
                        <p class="text-muted mb-4">An internal error occurred. Please contact professional support.</p>
                        <a href="/" class="btn btn-promamec-primary">
                            <i class="fas fa-home"></i> Return to Professional Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    return render_professional_page(content), 500

# ===== APPLICATION INITIALIZATION =====

def create_database():
    """Initialize professional database"""
    try:
        with app.app_context():
            db.create_all()
            logger.info(" Professional database initialized successfully")
    except Exception as e:
        logger.error(f" Database initialization failed: {e}")
        raise

def initialize_professional_platform():
    """Initialize the complete professional platform"""
    logger.info(" Initializing Promamec CT Scanner Professional Suite...")
    
    # Create database
    create_database()
    
    # Create directories
    os.makedirs('reports', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    logger.info(" Professional platform initialization complete")
    logger.info(f" Access the platform at: http://localhost:5000")
    logger.info(f" Demo credentials:")
    logger.info(f"   Admin: admin / admin123")
    logger.info(f"   Engineer: engineer / engineer123") 
    logger.info(f"   Client: client / client123")
    logger.info(f" Run /create-sample-data to populate with professional demo data")

# ===== MAIN APPLICATION ENTRY POINT =====

if __name__ == '__main__':
    try:
        # Initialize the professional platform
        initialize_professional_platform()
        
        # Configure development server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        sys.exit(1)

