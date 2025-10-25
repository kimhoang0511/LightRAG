#!/usr/bin/env python3
"""
Script to fix embedding dimension mismatch error

Error: AssertionError: Embedding dim mismatch, expected: 1024, but loaded: 1536

This happens when you switch embedding models with different dimensions.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys


def check_vector_db_files(working_dir: str):
    """Check vector database files for embedding dimension"""
    
    print("=" * 70)
    print("Vector Database Dimension Checker")
    print("=" * 70)
    
    working_path = Path(working_dir)
    
    if not working_path.exists():
        print(f"\n✅ Working directory doesn't exist: {working_dir}")
        print("   This is a fresh start - no conflicts possible!")
        return True, []
    
    # Check for vector database files
    vdb_files = list(working_path.glob("vdb_*.json"))
    
    if not vdb_files:
        print(f"\n✅ No vector database files found in: {working_dir}")
        print("   This is a fresh start - no conflicts possible!")
        return True, []
    
    print(f"\n📁 Found {len(vdb_files)} vector database files:")
    
    has_mismatch = False
    file_info = []
    
    for vdb_file in vdb_files:
        try:
            with open(vdb_file, 'r') as f:
                data = json.load(f)
                
            embedding_dim = data.get('embedding_dim', 'unknown')
            num_records = len(data.get('data', []))
            
            print(f"\n   📄 {vdb_file.name}")
            print(f"      Embedding Dimension: {embedding_dim}")
            print(f"      Number of Records: {num_records}")
            
            file_info.append({
                'file': vdb_file,
                'dim': embedding_dim,
                'records': num_records
            })
            
            if embedding_dim != 1024 and embedding_dim != 'unknown':
                has_mismatch = True
                print(f"      ⚠️  MISMATCH: Expected 1024, found {embedding_dim}")
        
        except Exception as e:
            print(f"\n   ❌ Error reading {vdb_file.name}: {e}")
    
    return not has_mismatch, file_info


def backup_working_dir(working_dir: str) -> str:
    """Create a backup of the working directory"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{working_dir}_backup_{timestamp}"
    
    print(f"\n📦 Creating backup...")
    print(f"   Source: {working_dir}")
    print(f"   Backup: {backup_dir}")
    
    try:
        shutil.copytree(working_dir, backup_dir)
        print(f"   ✅ Backup created successfully!")
        return backup_dir
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        raise


def clean_working_dir(working_dir: str):
    """Remove the working directory"""
    
    print(f"\n🧹 Removing old data...")
    print(f"   Directory: {working_dir}")
    
    try:
        shutil.rmtree(working_dir)
        print(f"   ✅ Directory removed successfully!")
    except Exception as e:
        print(f"   ❌ Failed to remove directory: {e}")
        raise


def main():
    # Get working directory from environment or use default
    working_dir = os.getenv("WORKING_DIR", "./rag_storage")
    
    print(f"\n🔍 Checking: {working_dir}")
    
    # Check vector database files
    is_ok, file_info = check_vector_db_files(working_dir)
    
    if is_ok:
        print("\n" + "=" * 70)
        print("✅ NO DIMENSION MISMATCH FOUND")
        print("=" * 70)
        print("\nYour vector database is compatible with Vietnamese_Embedding (1024 dim)")
        print("You can start the server without issues!")
        return 0
    
    # Found mismatch
    print("\n" + "=" * 70)
    print("❌ DIMENSION MISMATCH DETECTED")
    print("=" * 70)
    
    print("\n📋 Summary:")
    print("   Your vector database was created with a different embedding model.")
    print("   Vietnamese_Embedding requires 1024 dimensions.")
    
    print("\n💡 Options:")
    print("   1. Delete old data and start fresh (RECOMMENDED)")
    print("   2. Keep old data and use original embedding model")
    print("   3. Manually migrate data (advanced)")
    
    print("\n⚠️  WARNING: You cannot mix different embedding dimensions!")
    print("   If you switch models, you must rebuild the database.")
    
    # Ask user what to do
    print("\n" + "=" * 70)
    response = input("Do you want to DELETE old data and start fresh? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Aborted by user")
        print("\nTo keep using your old data:")
        print("   1. Check which embedding model created it (probably 1536 dim)")
        print("   2. Update .env to use that model instead")
        print("   3. Set EMBEDDING_DIM=1536")
        return 1
    
    # Create backup
    try:
        backup_dir = backup_working_dir(working_dir)
        print(f"\n✅ Backup saved at: {backup_dir}")
        print("   You can restore it later if needed")
    except Exception as e:
        print(f"\n❌ Cannot proceed without backup: {e}")
        return 1
    
    # Clean old data
    try:
        clean_working_dir(working_dir)
        print("\n✅ Old data removed!")
    except Exception as e:
        print(f"\n❌ Failed to clean: {e}")
        print(f"   Your backup is still safe at: {backup_dir}")
        return 1
    
    # Success
    print("\n" + "=" * 70)
    print("🎉 SUCCESS - Ready for Vietnamese_Embedding!")
    print("=" * 70)
    
    print("\n✅ What happened:")
    print(f"   1. Old data backed up to: {backup_dir}")
    print(f"   2. Working directory cleaned: {working_dir}")
    print("   3. Ready for fresh start with Vietnamese_Embedding (1024 dim)")
    
    print("\n🚀 Next steps:")
    print("   1. Verify your .env has:")
    print("      EMBEDDING_BINDING=vietnamese")
    print("      EMBEDDING_MODEL=AITeamVN/Vietnamese_Embedding")
    print("      EMBEDDING_DIM=1024")
    print("   2. Start your server: lightrag-server")
    print("   3. Insert documents - they will use Vietnamese_Embedding")
    
    print("\n💾 To restore old data (if needed):")
    print(f"   1. Stop server")
    print(f"   2. rm -rf {working_dir}")
    print(f"   3. mv {backup_dir} {working_dir}")
    print(f"   4. Update .env to use original embedding model")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
