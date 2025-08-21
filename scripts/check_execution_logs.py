import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='agenticai_platform', user='agenticai_user', password='agenticai_password')
cur = conn.cursor()

cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mcp_execution_logs' ORDER BY ordinal_position")
print('MCP Execution Logs columns:', [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
