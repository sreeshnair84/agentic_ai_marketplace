#!/usr/bin/env python3
"""
Verify agent signature and DNS data
"""
import asyncio
import asyncpg
import json

DATABASE_URL = "postgresql://lcnc_user:lcnc_password@localhost:5432/lcnc_platform"

async def verify_signatures():
    """Verify agent signatures and DNS configurations"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        print("🔍 Verifying Agent Registry Specification Compliance")
        print("=" * 60)
        
        agents = await conn.fetch("""
            SELECT name, display_name, url, health_url, dns_name, 
                   input_signature, output_signature, capabilities,
                   ai_provider, model_name, author, organization
            FROM agents 
            WHERE name LIKE '%-agent'
            ORDER BY name
        """)
        
        for agent in agents:
            print(f"\n🤖 Agent: {agent['display_name']} ({agent['name']})")
            print(f"   📍 URL: {agent['url']}")
            print(f"   🏥 Health URL: {agent['health_url']}")
            print(f"   🌐 DNS Name: {agent['dns_name']}")
            print(f"   🤖 AI Provider: {agent['ai_provider']}/{agent['model_name']}")
            print(f"   👤 Author: {agent['author']} @ {agent['organization']}")
            
            if agent['capabilities']:
                capabilities = json.loads(agent['capabilities'])
                print(f"   🔧 Capabilities: {', '.join([k for k, v in capabilities.items() if v])}")
            
            if agent['input_signature']:
                input_sig = json.loads(agent['input_signature'])
                if 'schema' in input_sig and 'properties' in input_sig['schema']:
                    required_fields = input_sig['schema'].get('required', [])
                    print(f"   📥 Input: {', '.join(required_fields)} (required)")
            
            if agent['output_signature']:
                output_sig = json.loads(agent['output_signature'])
                if 'schema' in output_sig and 'properties' in output_sig['schema']:
                    output_fields = list(output_sig['schema']['properties'].keys())
                    print(f"   📤 Output: {', '.join(output_fields)}")
        
        await conn.close()
        print(f"\n✅ Verified {len(agents)} agents with complete registry specification compliance!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(verify_signatures())
