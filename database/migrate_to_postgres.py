"""
Migration script: JSON or MongoDB → PostgreSQL
Migrates existing data to PostgreSQL. Run from project root with DATABASE_URL set.
"""

import json
import os
import sys
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.json_adapter import JSONAdapter
from database.postgresql_adapter import PostgreSQLAdapter

try:
    from shared.logger import setup_logger
    logger = setup_logger('migrate_to_postgres')
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('migrate_to_postgres')


def _get_source_adapter(source='json'):
    """Get source adapter: 'json' (default) or 'mongodb'."""
    if source == 'mongodb':
        from database.mongodb_adapter import MongoDBAdapter
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DATABASE', 'smart_attendance')
        return MongoDBAdapter(connection_uri=uri, database_name=db_name)
    base_dir = os.getenv('JSON_BASE_DIR', 'static')
    return JSONAdapter(base_dir=base_dir)


def migrate_to_postgres(source='json'):
    """Migrate all data from JSON (or MongoDB) to PostgreSQL."""
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/smart_attendance')
    logger.info("Starting %s → PostgreSQL migration...", source.upper())

    try:
        source_adapter = _get_source_adapter(source)
        pg_adapter = PostgreSQLAdapter(connection_url=database_url)
        logger.info("Adapters created successfully")

        # Migrate students
        logger.info("Migrating students...")
        students = source_adapter.get_students()
        for student in students:
            try:
                pg_adapter.create_student(student)
                logger.info("Migrated student: %s", student.get('student_id'))
            except Exception as e:
                logger.warning("Could not migrate student %s: %s", student.get('student_id'), e)

        # Migrate attendance records
        logger.info("Migrating attendance records...")
        records = source_adapter.get_attendance_records()
        for record in records:
            try:
                record = dict(record)
                ts = record.get('timestamp')
                if isinstance(ts, str):
                    try:
                        record['timestamp'] = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except ValueError:
                        pass
                pg_adapter.create_attendance_record(record)
                logger.info("Migrated attendance record for: %s", record.get('student_id'))
            except Exception as e:
                logger.warning("Could not migrate attendance record: %s", e)

        # Migrate users
        logger.info("Migrating users...")
        users = source_adapter.get_users()
        for user in users:
            try:
                pg_adapter.create_user(user)
                logger.info("Migrated user: %s", user.get('username'))
            except Exception as e:
                logger.warning("Could not migrate user %s: %s", user.get('username'), e)

        # Migrate courses
        logger.info("Migrating courses...")
        courses = source_adapter.get_courses()
        for course in courses:
            try:
                pg_adapter.create_course(course)
                logger.info("Migrated course: %s", course.get('code'))
            except Exception as e:
                logger.warning("Could not migrate course: %s", e)

        # Migrate rooms
        logger.info("Migrating rooms...")
        rooms = source_adapter.get_rooms()
        for room in rooms:
            try:
                pg_adapter.create_room(room)
                logger.info("Migrated room: %s", room.get('name'))
            except Exception as e:
                logger.warning("Could not migrate room: %s", e)

        # Migrate attendance sessions
        logger.info("Migrating attendance sessions...")
        sessions = source_adapter.get_sessions()
        for session in sessions:
            try:
                pg_adapter.create_session(session)
                logger.info("Migrated session: %s", session.get('id'))
            except Exception as e:
                logger.warning("Could not migrate session: %s", e)

        # Migrate cancellations
        logger.info("Migrating cancellations...")
        cancellations = source_adapter.get_cancellations()
        for cancellation in cancellations:
            try:
                pg_adapter.create_cancellation(cancellation)
                logger.info("Migrated cancellation: %s", cancellation.get('id'))
            except Exception as e:
                logger.warning("Could not migrate cancellation: %s", e)

        # Migrate excuses
        logger.info("Migrating excuses...")
        excuses = source_adapter.get_excuses()
        for excuse in excuses:
            try:
                pg_adapter.create_excuse(excuse)
                logger.info("Migrated excuse: %s", excuse.get('id'))
            except Exception as e:
                logger.warning("Could not migrate excuse: %s", e)

        logger.info("Migration completed successfully!")
        logger.info(
            "Migrated: %d students, %d attendance records, %d users, %d courses, %d rooms, "
            "%d sessions, %d cancellations, %d excuses",
            len(students), len(records), len(users), len(courses), len(rooms),
            len(sessions), len(cancellations), len(excuses)
        )
        return True

    except Exception as e:
        logger.error("Migration failed: %s", e, exc_info=True)
        return False


def backup_json_data():
    """Create a backup of JSON data before migration."""
    logger.info("Creating backup of JSON data...")
    backup_dir = os.path.join(
        os.path.dirname(__file__), '..',
        f"backups/json_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    os.makedirs(backup_dir, exist_ok=True)
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    files_to_backup = [
        ('students.json', {}),
        (os.path.join('attendance', 'records.json'), []),
        ('users.json', {}),
        ('courses.json', []),
        ('rooms.json', []),
        ('sessions.json', []),
        ('cancellations.json', []),
        ('excuses.json', []),
    ]
    for file_path, default in files_to_backup:
        full_path = os.path.join(static_dir, file_path)
        if os.path.exists(full_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            try:
                with open(full_path, 'r', encoding='utf-8') as src:
                    data = json.load(src)
            except (json.JSONDecodeError, IOError):
                data = default
            with open(backup_path, 'w', encoding='utf-8') as dst:
                json.dump(data, dst, ensure_ascii=False, indent=2)
            logger.info("Backed up: %s → %s", full_path, backup_path)
    logger.info("Backup created at: %s", backup_dir)
    return backup_dir


def verify_migration(source='json'):
    """Verify that migration was successful by comparing counts."""
    logger.info("Verifying migration...")
    try:
        source_adapter = _get_source_adapter(source)
        database_url = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/smart_attendance')
        pg_adapter = PostgreSQLAdapter(connection_url=database_url)

        src_students = len(source_adapter.get_students())
        pg_students = len(pg_adapter.get_students())
        src_records = len(source_adapter.get_attendance_records())
        pg_records = len(pg_adapter.get_attendance_records())
        src_users = len(source_adapter.get_users())
        pg_users = len(pg_adapter.get_users())

        logger.info("Students: source=%d, PostgreSQL=%d", src_students, pg_students)
        logger.info("Attendance: source=%d, PostgreSQL=%d", src_records, pg_records)
        logger.info("Users: source=%d, PostgreSQL=%d", src_users, pg_users)

        if src_students == pg_students and src_records == pg_records and src_users == pg_users:
            logger.info("Verification successful: counts match.")
            return True
        logger.warning("Verification warning: counts do not match exactly.")
        return False
    except Exception as e:
        logger.error("Verification failed: %s", e)
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Smart Attendance System - Data Migration to PostgreSQL")
    print("=" * 60)
    print()

    source = os.getenv('MIGRATE_FROM', 'json').lower()
    if source not in ('json', 'mongodb'):
        source = 'json'
    print("Source: %s" % source)
    print("Target: PostgreSQL (%s)" % os.getenv('DATABASE_URL', 'postgresql://localhost:5432/smart_attendance'))
    print()

    if not os.getenv('DATABASE_URL'):
        print("Warning: DATABASE_URL is not set. Using default: postgresql://localhost:5432/smart_attendance")
        print()

    response = input("Do you want to proceed with migration? (yes/no): ")
    if response.lower() not in ('yes', 'y'):
        print("Migration cancelled.")
        sys.exit(0)
    print()

    if source == 'json':
        backup_dir = backup_json_data()
        print()
    else:
        backup_dir = None

    success = migrate_to_postgres(source=source)
    print()

    if success:
        verify_migration(source=source)
        print()
        print("=" * 60)
        print("Migration completed!")
        if backup_dir:
            print("Backup saved at: %s" % backup_dir)
        print()
        print("Next steps:")
        print("1. Set in .env: USE_POSTGRESQL=true")
        print("2. Set DATABASE_URL=postgresql://user:password@host:5432/smart_attendance")
        print("3. Restart the application")
        print("=" * 60)
    else:
        print("=" * 60)
        print("Migration failed!")
        if backup_dir:
            print("Your data is safe in: %s" % backup_dir)
        print("=" * 60)
        sys.exit(1)
