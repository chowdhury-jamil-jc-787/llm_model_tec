# generate_schema.py
import pymysql

connection = pymysql.connect(
    host='atpldhaka.com',
    user='atpldhaka_tecerp',
    password='atpldhaka_tecerp',
    db='atpldhaka_tecerp',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

schema_lines = []

try:
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        tables = [row[f'Tables_in_atpldhaka_tecerp'] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            col_names = [col['Field'] for col in columns]
            schema_lines.append(f"{table}: {', '.join(col_names)}")

finally:
    connection.close()

with open("schema.txt", "w") as f:
    f.write("\n".join(schema_lines))

print("✅ schema.txt generated successfully.")
