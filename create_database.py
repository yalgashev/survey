"""
Script to create the PostgreSQL database
Run this before running migrations
"""
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    # Database configuration
    DB_NAME = 'survey_db'
    DB_USER = 'postgres'
    DB_PASSWORD = '123456789'
    DB_HOST = 'localhost'
    DB_PORT = '5433'  # PostgreSQL 18 might use port 5433
    
    try:
        # Connect to PostgreSQL server (to 'postgres' database)
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname='postgres',  # Connect to default database
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database already exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"✓ Database '{DB_NAME}' already exists!")
        else:
            # Create database
            print(f"Creating database '{DB_NAME}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            ))
            print(f"✓ Database '{DB_NAME}' created successfully!")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*50)
        print("✓ Database setup complete!")
        print("="*50)
        print("\nNext steps:")
        print("1. Run: python manage.py makemigrations")
        print("2. Run: python manage.py migrate")
        print("3. Run: python manage.py createsuperuser")
        print("4. Run: python manage.py runserver")
        
    except psycopg2.Error as e:
        print(f"✗ Error: {e}")
        print("\nPlease check:")
        print("1. PostgreSQL is running")
        print("2. Username and password are correct")
        print("3. PostgreSQL is accessible on localhost:5432")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == '__main__':
    create_database()
