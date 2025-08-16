#!/usr/bin/env python3
"""
Migration Cleanup Script
Archives old migration scripts and individual setup files since they're now consolidated into initial_setup.py
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_migrations():
    """Archive old migration scripts"""
    
    project_root = Path(__file__).parent
    
    # Create archive directory
    archive_dir = project_root / "archive" / f"migration_scripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creating archive at: {archive_dir}")
    
    # Files to archive
    files_to_archive = [
        "run_migration.py",
        "run_agent_migration.py", 
        "run_tools_workflows_migration.py",
        "setup_dev.py",
        "setup_llm_management.py",
        "create_admin.py",
        "create_admin_with_secret123.py",
        "fix_admin_role.py",
        "add_sample_data.py",
        "check_agents.py",
        "check_db.py",
        "check_schema.py", 
        "check_tools_workflows.py",
        "debug_db.py",
        "insert_agents.py"
    ]
    
    archived_count = 0
    
    for filename in files_to_archive:
        file_path = project_root / filename
        if file_path.exists():
            # Copy to archive
            archive_path = archive_dir / filename
            shutil.copy2(file_path, archive_path)
            
            # Remove original
            file_path.unlink()
            
            print(f"✅ Archived: {filename}")
            archived_count += 1
        else:
            print(f"⚠️  Not found: {filename}")
    
    # Create README in archive
    readme_content = f"""# Archived Migration Scripts

These files were archived on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} when consolidating 
all migration and setup logic into `initial_setup.py`.

## Archived Files ({archived_count} total)

### Migration Scripts
- `run_migration.py` - Applied 0005_sample_queries_system.sql
- `run_agent_migration.py` - Applied agent registry fields migration
- `run_tools_workflows_migration.py` - Applied tools/workflows registry migration

### Setup Scripts  
- `setup_dev.py` - Development environment setup
- `setup_llm_management.py` - LLM management system setup

### Data Scripts
- `create_admin.py` - Created admin user
- `create_admin_with_secret123.py` - Created admin with specific password
- `fix_admin_role.py` - Fixed admin role assignment
- `add_sample_data.py` - Added sample data
- `insert_agents.py` - Inserted sample agents

### Debug/Check Scripts
- `check_agents.py` - Checked agent data
- `check_db.py` - Checked database connectivity
- `check_schema.py` - Verified schema
- `check_tools_workflows.py` - Checked tools/workflows
- `debug_db.py` - Database debugging

## Replacement

All functionality from these scripts has been consolidated into:
- `initial_setup.py` - Complete platform setup for fresh installations
- `verify_setup.py` - Setup verification (auto-generated)

## Recovery

If you need to recover any of these scripts, they are preserved in this archive directory.
The migration SQL files remain in `infra/migrations/` for reference.
"""
    
    readme_path = archive_dir / "README.md"
    readme_path.write_text(readme_content)
    
    print(f"\n📋 Created archive README")
    print(f"📁 Archive location: {archive_dir.relative_to(project_root)}")
    print(f"✅ Successfully archived {archived_count} files")
    
    # Update main README
    update_main_readme(project_root)

def update_main_readme(project_root: Path):
    """Update main README to reference the new setup process"""
    
    readme_path = project_root / "README.md"
    
    if readme_path.exists():
        # Read current README
        content = readme_path.read_text()
        
        # Add setup section if not present
        setup_section = """
## Quick Setup (Fresh Installation)

For a completely new installation, use the consolidated setup script:

```bash
# Run the initial setup script
python initial_setup.py

# Verify the setup
python verify_setup.py
```

This replaces all individual migration and setup scripts with a single comprehensive setup process.

"""
        
        # Check if setup section already exists
        if "initial_setup.py" not in content:
            # Insert after the first heading
            lines = content.split('\n')
            insert_pos = 1  # After first line (title)
            
            for i, line in enumerate(lines):
                if line.startswith('##') and i > 0:
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, setup_section)
            
            # Write back
            readme_path.write_text('\n'.join(lines))
            print("📝 Updated README.md with new setup instructions")

def main():
    """Main cleanup function"""
    
    print("🧹 Migration Cleanup Script")
    print("=" * 40)
    
    try:
        response = input("Archive old migration scripts? This will move them to an archive folder. (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Cleanup cancelled.")
            return
    except KeyboardInterrupt:
        print("\nCleanup cancelled.")
        return
    
    cleanup_migrations()
    
    print("\n" + "=" * 40)
    print("🎉 Cleanup Complete!")
    print("\nOld migration scripts have been archived.")
    print("Use `python initial_setup.py` for fresh installations.")
    print("Archived scripts remain available for reference.")

if __name__ == "__main__":
    main()
