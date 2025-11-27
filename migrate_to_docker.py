"""
Migrate data from old PostgreSQL database (port 5433) to Docker database (port 5432)
"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Source database (local PostgreSQL 18 on port 5433)
SOURCE = {
    'dbname': 'survey_db',
    'user': 'postgres',
    'password': '123456789',
    'host': 'localhost',
    'port': '5433'
}

# Target database (Docker PostgreSQL 16 on port 5432)
TARGET = {
    'dbname': 'survey_db',
    'user': 'postgres',
    'password': '123456789',
    'host': 'localhost',
    'port': '5432'
}

def migrate_data():
    print("Connecting to source database (port 5433)...")
    src_conn = psycopg2.connect(**SOURCE, cursor_factory=RealDictCursor)
    src_cur = src_conn.cursor()
    
    print("Connecting to target database (Docker port 5432)...")
    tgt_conn = psycopg2.connect(**TARGET)
    tgt_cur = tgt_conn.cursor()
    
    # Migrate Schools
    print("\nMigrating Schools...")
    src_cur.execute("SELECT * FROM evaluations_school ORDER BY id")
    schools = src_cur.fetchall()
    for school in schools:
        tgt_cur.execute(
            "INSERT INTO evaluations_school (id, name, code, description, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (school['id'], school['name'], school['code'], school['description'],
             school['created_at'], school['updated_at'])
        )
    print(f"✓ Migrated {len(schools)} schools")
    
    # Migrate Departments
    print("Migrating Departments...")
    src_cur.execute("SELECT * FROM evaluations_department ORDER BY id")
    departments = src_cur.fetchall()
    for dept in departments:
        tgt_cur.execute(
            "INSERT INTO evaluations_department (id, name, code, description, school_id, created_at, updated_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (dept['id'], dept['name'], dept['code'], dept['description'], dept['school_id'],
             dept['created_at'], dept['updated_at'])
        )
    print(f"✓ Migrated {len(departments)} departments")
    
    # Migrate Groups
    print("Migrating Groups...")
    src_cur.execute("SELECT * FROM evaluations_group ORDER BY id")
    groups = src_cur.fetchall()
    for group in groups:
        tgt_cur.execute(
            "INSERT INTO evaluations_group (id, group_name, department_id, total_students, participated_students) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (group['id'], group['group_name'], group['department_id'],
             group['total_students'], group['participated_students'])
        )
    print(f"✓ Migrated {len(groups)} groups")
    
    # Migrate Professors
    print("Migrating Professors...")
    src_cur.execute("SELECT * FROM evaluations_professor ORDER BY id")
    professors = src_cur.fetchall()
    for prof in professors:
        tgt_cur.execute(
            "INSERT INTO evaluations_professor (id, full_name, email, school_id) "
            "VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (prof['id'], prof['full_name'], prof['email'], prof['school_id'])
        )
    print(f"✓ Migrated {len(professors)} professors")
    
    # Migrate GroupProfessor assignments
    print("Migrating Professor-Group assignments...")
    src_cur.execute("SELECT * FROM evaluations_groupprofessor ORDER BY id")
    assignments = src_cur.fetchall()
    for assignment in assignments:
        tgt_cur.execute(
            "INSERT INTO evaluations_groupprofessor (id, group_id, professor_id) "
            "VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (assignment['id'], assignment['group_id'], assignment['professor_id'])
        )
    print(f"✓ Migrated {len(assignments)} professor-group assignments")
    
    # Migrate Surveys
    print("Migrating Surveys...")
    src_cur.execute("SELECT * FROM evaluations_survey ORDER BY id")
    surveys = src_cur.fetchall()
    for survey in surveys:
        tgt_cur.execute(
            "INSERT INTO evaluations_survey (id, group_id, professor_id, academic_performance, "
            "classroom_management, communication_skills, fairness, overall_satisfaction, comments, created_at) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (survey['id'], survey['group_id'], survey['professor_id'], survey['academic_performance'],
             survey['classroom_management'], survey['communication_skills'], survey['fairness'],
             survey['overall_satisfaction'], survey['comments'], survey['created_at'])
        )
    print(f"✓ Migrated {len(surveys)} surveys")
    
    # Update sequences
    print("\nUpdating ID sequences...")
    for table, id_col in [
        ('evaluations_school', 'id'),
        ('evaluations_department', 'id'),
        ('evaluations_group', 'id'),
        ('evaluations_professor', 'id'),
        ('evaluations_groupprofessor', 'id'),
        ('evaluations_survey', 'id'),
    ]:
        tgt_cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', '{id_col}'), COALESCE(MAX({id_col}), 1)) FROM {table}")
    
    tgt_conn.commit()
    
    print("\n" + "="*50)
    print("✓ Data migration completed successfully!")
    print("="*50)
    
    src_cur.close()
    src_conn.close()
    tgt_cur.close()
    tgt_conn.close()

if __name__ == "__main__":
    try:
        migrate_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
