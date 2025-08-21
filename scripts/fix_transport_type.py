import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='agenticai_platform', user='agenticai_user', password='agenticai_password')
cur = conn.cursor()

cur.execute("UPDATE mcp_servers SET transport_type = 'sse' WHERE transport_type = 'http'")
conn.commit()
print('✅ Updated transport_type to valid enum value')

cur.close()
conn.close()
