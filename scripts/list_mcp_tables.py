import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='agenticai_platform', user='agenticai_user', password='agenticai_password')
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'mcp%' ORDER BY table_name")
print('MCP Tables:', [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
