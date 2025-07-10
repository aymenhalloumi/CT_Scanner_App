#!/usr/bin/env python3
"""
Promamec CT Scanner Professional Suite - Compatibility Checker
Verify your existing setup is ready for CT Scanner integration
"""

import sys
import os
import importlib
from packaging import version

def check_python_version():
    """Check Python version"""
    print("🐍 Python Version Check:")
    current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {current_version} - Compatible")
        return True
    else:
        print(f"   ❌ Python {current_version} - Requires Python 3.8+")
        return False

def check_existing_packages():
    """Check your existing Flask packages"""
    print("\n📦 Existing Package Check:")
    
    required_packages = {
        'flask': ('Flask', '2.0.0'),
        'flask_sqlalchemy': ('Flask-SQLAlchemy', '2.0.0'),
        'flask_login': ('Flask-Login', '0.5.0'),
        'flask_admin': ('Flask-Admin', '1.6.0'),
        'flask_wtf': ('Flask-WTF', '1.0.0'),
        'wtforms': ('WTForms', '3.0.0'),
        'openai': ('OpenAI', '1.0.0'),
        'requests': ('requests', '2.20.0'),
        'sqlalchemy': ('SQLAlchemy', '1.4.0')
    }
    
    all_good = True
    
    for package, (name, min_version) in required_packages.items():
        try:
            module = importlib.import_module(package)
            if hasattr(module, '__version__'):
                current_version = module.__version__
                if version.parse(current_version) >= version.parse(min_version):
                    print(f"   ✅ {name} {current_version} - Compatible")
                else:
                    print(f"   ⚠️  {name} {current_version} - Minimum {min_version} recommended")
            else:
                print(f"   ✅ {name} - Available (version unknown)")
        except ImportError:
            print(f"   ❌ {name} - Missing (should be in your requirements.txt)")
            all_good = False
    
    return all_good

def check_additional_packages():
    """Check packages needed for CT Scanner features"""
    print("\n🎨 Additional Packages for CT Scanner:")
    
    additional_packages = {
        'plotly': 'Plotly (3D visualization)',
        'matplotlib': 'Matplotlib (charts and graphs)', 
        'reportlab': 'ReportLab (PDF generation)',
        'PIL': 'Pillow (image processing)',
        'seaborn': 'Seaborn (enhanced charts)',
        'dateutil': 'python-dateutil (date utilities)'
    }
    
    missing_packages = []
    
    for package, description in additional_packages.items():
        try:
            importlib.import_module(package)
            print(f"   ✅ {description} - Available")
        except ImportError:
            print(f"   ❌ {description} - Missing")
            missing_packages.append(package)
    
    return missing_packages

def check_environment():
    """Check environment configuration"""
    print("\n🔧 Environment Configuration:")
    
    # Check OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key and openai_key != 'your-openai-api-key-here':
        print("   ✅ OpenAI API key - Configured")
    else:
        print("   ⚠️  OpenAI API key - Not configured (AI features will be limited)")
    
    # Check if running in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ Virtual environment - Active")
    else:
        print("   ⚠️  Virtual environment - Not detected (recommended)")
    
    return True

def provide_installation_instructions(missing_packages):
    """Provide installation instructions"""
    print("\n" + "="*60)
    print("📋 INSTALLATION INSTRUCTIONS")
    print("="*60)
    
    if missing_packages:
        print("\n🔧 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        
        print("\n📝 Or add to your requirements.txt:")
        package_versions = {
            'plotly': 'plotly==5.17.0',
            'matplotlib': 'matplotlib==3.8.2',
            'reportlab': 'reportlab==4.0.7', 
            'PIL': 'Pillow==10.1.0',
            'seaborn': 'seaborn==0.13.0',
            'dateutil': 'python-dateutil==2.8.2'
        }
        
        for package in missing_packages:
            if package in package_versions:
                print(f"   {package_versions[package]}")
            else:
                print(f"   {package}")
    
    print("\n🚀 After installing packages:")
    print("   1. Copy app.py to your project directory")
    print("   2. Run: python app.py")
    print("   3. Visit: http://localhost:5000")
    print("   4. Go to: /create-sample-data (for demo)")
    
    print("\n🔑 Optional - Configure OpenAI for AI features:")
    print("   export OPENAI_API_KEY=your-api-key-here")
    print("   # Or add to .env file")

def main():
    """Main compatibility check"""
    print("🏥 Promamec CT Scanner Professional Suite")
    print("🔍 Compatibility Checker")
    print("="*60)
    
    # Run all checks
    python_ok = check_python_version()
    packages_ok = check_existing_packages() 
    missing_additional = check_additional_packages()
    env_ok = check_environment()
    
    print("\n" + "="*60)
    print("📊 COMPATIBILITY SUMMARY")
    print("="*60)
    
    if python_ok and packages_ok:
        print("✅ Core Requirements: PASSED")
        print("   Your existing Flask setup is compatible!")
    else:
        print("❌ Core Requirements: FAILED")
        print("   Please check your Flask installation")
    
    if not missing_additional:
        print("✅ Additional Packages: ALL INSTALLED")
        print("   Ready to run CT Scanner Professional Suite!")
    else:
        print(f"⚠️  Additional Packages: {len(missing_additional)} missing")
        print("   Install missing packages to enable all features")
    
    # Overall status
    if python_ok and packages_ok and not missing_additional:
        print("\n🎉 STATUS: READY TO GO!")
        print("   Your system is fully compatible with CT Scanner Professional Suite")
        print("   Next steps:")
        print("   1. Copy app.py to your project")
        print("   2. Run: python app.py")
        print("   3. Visit: http://localhost:5000/create-sample-data")
    else:
        print("\n🔧 STATUS: NEEDS SETUP")
        provide_installation_instructions(missing_additional)
    
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Compatibility check failed: {e}")
        print("💡 Make sure you're in your project's virtual environment")
        sys.exit(1)
