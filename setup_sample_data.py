# Setup and Database Initialization Script
# Run this script to set up the project with sample data

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from evaluations.models import Group, Professor, GroupProfessor

def setup_sample_data():
    """Create sample data for testing"""
    
    print("Creating sample groups...")
    groups = [
        Group.objects.get_or_create(
            group_name="CS-101",
            defaults={'department': 'Computer Science', 'total_students': 30}
        )[0],
        Group.objects.get_or_create(
            group_name="CS-102",
            defaults={'department': 'Computer Science', 'total_students': 28}
        )[0],
        Group.objects.get_or_create(
            group_name="ENG-201",
            defaults={'department': 'Engineering', 'total_students': 35}
        )[0],
    ]
    print(f"✓ Created {len(groups)} groups")
    
    print("\nCreating sample professors...")
    professors = [
        Professor.objects.get_or_create(
            full_name="Dr. John Smith",
            defaults={'department': 'Computer Science'}
        )[0],
        Professor.objects.get_or_create(
            full_name="Prof. Sarah Johnson",
            defaults={'department': 'Computer Science'}
        )[0],
        Professor.objects.get_or_create(
            full_name="Dr. Michael Brown",
            defaults={'department': 'Engineering'}
        )[0],
        Professor.objects.get_or_create(
            full_name="Prof. Emily Davis",
            defaults={'department': 'Engineering'}
        )[0],
    ]
    print(f"✓ Created {len(professors)} professors")
    
    print("\nAssigning professors to groups...")
    assignments = [
        # CS-101 taught by Dr. Smith and Prof. Johnson
        GroupProfessor.objects.get_or_create(
            group=groups[0], professor=professors[0]
        ),
        GroupProfessor.objects.get_or_create(
            group=groups[0], professor=professors[1]
        ),
        # CS-102 taught by Prof. Johnson
        GroupProfessor.objects.get_or_create(
            group=groups[1], professor=professors[1]
        ),
        # ENG-201 taught by Dr. Brown and Prof. Davis
        GroupProfessor.objects.get_or_create(
            group=groups[2], professor=professors[2]
        ),
        GroupProfessor.objects.get_or_create(
            group=groups[2], professor=professors[3]
        ),
    ]
    print(f"✓ Created {len(assignments)} professor-group assignments")
    
    print("\n" + "="*50)
    print("✓ Sample data setup completed successfully!")
    print("="*50)
    print("\nYou can now:")
    print("1. Run: python manage.py runserver")
    print("2. Visit: http://localhost:8000")
    print("3. Admin: http://localhost:8000/admin")
    print("4. Hidden Edit: http://localhost:8000/edit/")

if __name__ == '__main__':
    setup_sample_data()
