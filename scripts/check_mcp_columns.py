import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='agenticai_platform', user='agenticai_user', password='agenticai_password')
cur = conn.cursor()

# Check MCP servers table structure
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mcp_servers' ORDER BY ordinal_position")
print('MCP Servers columns:', [row[0] for row in cur.fetchall()])

# Check MCP endpoints table structure  
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mcp_endpoints' ORDER BY ordinal_position")
print('MCP Endpoints columns:', [row[0] for row in cur.fetchall()])

# Check MCP tools table structure
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'mcp_tools_registry' ORDER BY ordinal_position")
print('MCP Tools columns:', [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
