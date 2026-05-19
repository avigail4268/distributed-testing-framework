# File: db_analytics.py
import sqlite3
import pandas as pd


def run_analytics():
    # 1. Connect directly to the SQLite database file
    conn = sqlite3.connect("tasks.db")

    print("\n--- DISTRIBUTED TESTING ANALYTICS ---\n")

    # 2. Raw SQL Query: Calculate Success Rate and Average Duration
    # This query joins the tasks and results tables to give us a full picture
    sql_query = """
        SELECT 
            t.category as test_type,
            COUNT(r.id) as total_runs,
            SUM(CASE WHEN r.status = 'PASSED' THEN 1 ELSE 0 END) * 100.0 / COUNT(r.id) as success_rate_percent,
            ROUND(AVG(r.duration_seconds), 2) as avg_duration_sec
        FROM 
            tasks t
        LEFT JOIN 
            results r ON t.id = r.task_id
        WHERE 
            r.id IS NOT NULL
        GROUP BY 
            t.category;
    """

    # 3. Use Pandas to run the query and display it nicely as a table
    try:
        df = pd.read_sql_query(sql_query, conn)
        if df.empty:
            print("No test results found in the database yet.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Error running query: {e}")
    finally:
        conn.close()
        print("\n-------------------------------------\n")


if __name__ == "__main__":
    run_analytics()