from django.db import connections

def run_sql_on_laravel_db(sql):
    with connections['laravel'].cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
