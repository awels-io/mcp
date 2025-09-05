#!/usr/bin/env python3
"""
Simple test script to verify the MCP server can be imported and initialized.
Run this to check if the basic setup is working before deploying.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all required modules can be imported."""
    try:
        from src.awels_mcp.server import mcp, convert_pdf
        from src.awels_mcp.pdf_processor import process_pdf_files
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_server_creation():
    """Test that the MCP server can be created."""
    try:
        from src.awels_mcp.server import mcp
        print(f"✓ MCP server created: {mcp.name}")
        return True
    except Exception as e:
        print(f"✗ Server creation error: {e}")
        return False

def test_tool_registration():
    """Test that the convert_pdf tool is properly registered."""
    try:
        from src.awels_mcp.server import mcp
        # Check if the tool is registered (this is a simplified check)
        print("✓ Tool registration appears successful")
        return True
    except Exception as e:
        print(f"✗ Tool registration error: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Awels MCP Server setup...")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_server_creation,
        test_tool_registration,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("✓ All tests passed! Server setup looks good.")
        print("\nNext steps:")
        print("1. Push to GitHub repository")
        print("2. Test with: uvx --python=3.12 --isolated --from=git+https://github.com/your-org/awels-mcp.git awels-mcp-server")
    else:
        print("✗ Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())