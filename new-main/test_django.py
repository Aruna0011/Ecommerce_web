import os
import sys
import django

def setup_django():
    # Add the project directory to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
    django.setup()
    print("✅ Django setup complete")

def test_database():
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Database connection successful!")
            print(f"Database backend: {connection.vendor}")
            print(f"Database name: {connection.settings_dict['NAME']}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Django...")
    setup_django()
    
    print("\nTesting database connection...")
    test_database()
