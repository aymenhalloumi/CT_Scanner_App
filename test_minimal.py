# ================================================
# MINIMAL WORKING FLASK-APPBUILDER TEST
# Let's start with the absolute basics that MUST work
# ================================================

from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

# Create Flask app
app = Flask(__name__)

# Minimal configuration
app.config['SECRET_KEY'] = '062c2fae05e99855de618b4df4dd15cd7ee662312e2d725ac11928c2f0377adc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minimal_test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLA
db = SQLA(app)

# Initialize AppBuilder - This should create admin routes
appbuilder = AppBuilder(app, db.session)

@app.route('/')
def index():
    return '''
    <h1>🧪 Minimal Flask-AppBuilder Test</h1>
    <p><a href="/admin/">Admin Interface</a></p>
    <p><a href="/login/">Login</a></p>
    <p><a href="/debug-routes">Debug Routes</a></p>
    '''

@app.route('/debug-routes')
def debug_routes():
    """Show all available routes"""
    output = ["<h2>🔍 Available Routes</h2>"]
    admin_routes = []
    other_routes = []
    
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        route_info = f"<strong>{rule.endpoint}</strong>: {rule.rule} [{methods}]"
        
        if '/admin' in rule.rule or rule.endpoint.startswith('Security'):
            admin_routes.append(route_info)
        else:
            other_routes.append(route_info)
    
    output.append("<h3>🔧 Admin Routes:</h3>")
    if admin_routes:
        output.extend(sorted(admin_routes))
    else:
        output.append("<p style='color: red;'>❌ NO ADMIN ROUTES FOUND!</p>")
    
    output.append("<h3>📄 Other Routes:</h3>")
    output.extend(sorted(other_routes))
    
    return "<br>".join(output)

# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Minimal database created")

if __name__ == '__main__':
    print("🧪 Testing minimal Flask-AppBuilder setup...")
    print("🌐 Visit: http://localhost:5000")
    print("🔧 Admin: http://localhost:5000/admin/")
    print("🔍 Routes: http://localhost:5000/debug-routes")
    app.run(debug=True, host='0.0.0.0', port=5000)