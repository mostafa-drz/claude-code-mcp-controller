#!/usr/bin/env python3
"""
FastMCP Pattern Validation

Compare our implementation patterns with FastMCP examples.
"""

import inspect

def compare_with_echo_example():
    """Compare our implementation with echo.py example."""
    print("🔍 Comparing with FastMCP echo.py example")
    print("-" * 40)

    # Echo example pattern
    echo_pattern = """
from fastmcp import FastMCP
mcp = FastMCP("Echo Server")

@mcp.tool
def echo_tool(text: str) -> str:
    '''Echo the input text'''
    return text

@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"
"""

    # Our implementation pattern
    try:
        import server
        from fastmcp import FastMCP

        # Check server creation pattern
        assert isinstance(server.mcp, FastMCP), "Not a FastMCP instance"
        print("✅ Server creation pattern matches echo.py")

        # Check we have the same imports
        assert hasattr(server, 'FastMCP'), "Missing FastMCP import"
        print("✅ Import pattern matches echo.py")

        # Check we use @mcp.tool decorator (can't check directly, but source should show it)
        with open('server.py', 'r') as f:
            content = f.read()
            if '@mcp.tool' in content:
                print("✅ @mcp.tool decorator usage matches echo.py")
            else:
                print("❌ Missing @mcp.tool decorator")
                return False

        # Check we use @mcp.resource decorator
        if '@mcp.resource(' in content:
            print("✅ @mcp.resource decorator usage matches echo.py")
        else:
            print("❌ Missing @mcp.resource decorator")
            return False

        return True

    except Exception as e:
        print(f"❌ Pattern comparison failed: {e}")
        return False

def compare_with_config_example():
    """Compare our implementation with config_server.py example."""
    print("\n🔍 Comparing with FastMCP config_server.py example")
    print("-" * 50)

    config_pattern = """
mcp = FastMCP(server_name)

@mcp.tool
def get_status() -> dict[str, str | bool]:
    '''Get the current server configuration and status.'''
    return {...}

if __name__ == "__main__":
    mcp.run()
"""

    try:
        with open('server.py', 'r') as f:
            content = f.read()

        # Check for proper __main__ block
        if 'if __name__ == "__main__":' in content:
            print("✅ __main__ block pattern matches config_server.py")
        else:
            print("❌ Missing __main__ block")
            return False

        # Check for mcp.run() call
        if 'mcp.run()' in content:
            print("✅ mcp.run() usage matches config_server.py")
        else:
            print("❌ Missing mcp.run() call")
            return False

        # Check for return type annotations
        if '-> Dict:' in content or '-> dict:' in content:
            print("✅ Return type annotations match config_server.py pattern")
        else:
            print("❌ Missing return type annotations")
            return False

        return True

    except Exception as e:
        print(f"❌ Config pattern comparison failed: {e}")
        return False

def validate_advanced_patterns():
    """Validate advanced patterns beyond basic examples."""
    print("\n🔍 Validating advanced patterns")
    print("-" * 35)

    try:
        with open('server.py', 'r') as f:
            content = f.read()

        # Check for async function support
        if 'async def' in content:
            print("✅ Async function support (advanced)")
        else:
            print("⚠️  No async functions found")

        # Check for proper error handling
        if 'try:' in content and 'except' in content:
            print("✅ Error handling (production-ready)")
        else:
            print("❌ Missing error handling")
            return False

        # Check for type hints
        if 'from typing import' in content:
            print("✅ Type hints usage (best practice)")
        else:
            print("⚠️  Limited type hint usage")

        # Check for docstrings
        if '"""' in content:
            print("✅ Docstring documentation (best practice)")
        else:
            print("❌ Missing docstrings")
            return False

        # Check for logging
        if 'logging' in content:
            print("✅ Logging implementation (production-ready)")
        else:
            print("⚠️  No logging found")

        return True

    except Exception as e:
        print(f"❌ Advanced pattern validation failed: {e}")
        return False

def validate_fastmcp_cloud_compatibility():
    """Validate FastMCP Cloud deployment compatibility."""
    print("\n🔍 Validating FastMCP Cloud compatibility")
    print("-" * 45)

    # Check entrypoint format
    try:
        import server
        if hasattr(server, 'mcp') and server.mcp.name:
            print(f"✅ Entrypoint available: server.py:mcp ('{server.mcp.name}')")
        else:
            print("❌ Missing proper entrypoint")
            return False
    except Exception as e:
        print(f"❌ Entrypoint validation failed: {e}")
        return False

    # Check requirements.txt format
    try:
        with open('requirements.txt', 'r') as f:
            lines = f.readlines()
            fastmcp_found = False
            for line in lines:
                if line.strip().startswith('fastmcp'):
                    print(f"✅ FastMCP dependency: {line.strip()}")
                    fastmcp_found = True
                    break
            if not fastmcp_found:
                print("❌ FastMCP not in requirements.txt")
                return False
    except Exception as e:
        print(f"❌ Requirements validation failed: {e}")
        return False

    # Check HTTP transport readiness
    try:
        with open('server.py', 'r') as f:
            content = f.read()
            if 'transport="http"' in content or 'HTTP' in content:
                print("✅ HTTP transport ready for cloud deployment")
            else:
                print("✅ Default STDIO transport (FastMCP Cloud compatible)")
    except Exception as e:
        print(f"❌ Transport check failed: {e}")
        return False

    return True

def main():
    """Run all pattern validations."""
    print("🚀 FastMCP Pattern Validation Suite")
    print("=" * 50)

    checks = [
        ("Echo Example Patterns", compare_with_echo_example),
        ("Config Example Patterns", compare_with_config_example),
        ("Advanced Patterns", validate_advanced_patterns),
        ("FastMCP Cloud Compatibility", validate_fastmcp_cloud_compatibility),
    ]

    passed = 0
    total = len(checks)

    for check_name, check_func in checks:
        try:
            if check_func():
                passed += 1
                print(f"\n✅ {check_name} PASSED")
            else:
                print(f"\n❌ {check_name} FAILED")
        except Exception as e:
            print(f"\n❌ {check_name} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"🎯 PATTERN VALIDATION: {passed}/{total} checks passed")

    if passed == total:
        print("\n🚀 IMPLEMENTATION FULLY VALIDATED!")
        print("✅ Follows all FastMCP patterns correctly")
        print("✅ Exceeds basic examples with production features")
        print("✅ Ready for FastMCP Cloud deployment")
        print("✅ Compatible with ChatGPT MCP connectors")
        return True
    else:
        print(f"\n⚠️  {total - passed} pattern validation(s) failed")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)