#!/usr/bin/env python3
"""
Test script to demonstrate MicroPython Windows Unicode filename limitation.

Run this with mpremote to test Unicode handling:
    mpremote connect <device> run test_unicode_filenames.py

Or paste into REPL to test interactively.
"""

import os
import sys

print("=" * 60)
print("MicroPython Windows Unicode Filename Test")
print("=" * 60)
print(f"Platform: {sys.platform}")
print()

# Test 1: Unicode console output (WORKS)
print("TEST 1: Unicode Console Output")
print("-" * 40)
try:
    print("  print('café'): ", end="")
    print("café")
    print("  print('日本語'): ", end="")
    print("日本語")
    print("  print('José García'): ", end="")
    print("José García")
    print("  Result: ✅ PASS")
except Exception as e:
    print(f"  Result: ❌ FAIL - {type(e).__name__}: {e}")
print()

# Test 2: Unicode string operations (WORKS)
print("TEST 2: Unicode String Operations")
print("-" * 40)
try:
    s = "Adéọlá_Olúwadáre"
    print(f"  String: {s}")
    print(f"  Length: {len(s)}")
    print(f"  Upper: {s.upper()}")
    print(f"  Contains 'é': {'é' in s}")
    print("  Result: ✅ PASS")
except Exception as e:
    print(f"  Result: ❌ FAIL - {type(e).__name__}: {e}")
print()

# Test 3: ASCII filename operations (WORKS)
print("TEST 3: ASCII Filename Operations")
print("-" * 40)
try:
    # Create test file with ASCII name
    with open("_test_ascii.txt", "w") as f:
        f.write("Hello, World!")
    
    # Stat it
    st = os.stat("_test_ascii.txt")
    print(f"  Created: _test_ascii.txt")
    print(f"  Size: {st[6]} bytes")
    
    # Read it back
    with open("_test_ascii.txt", "r") as f:
        content = f.read()
    print(f"  Content: {content}")
    
    # Clean up
    os.remove("_test_ascii.txt")
    print("  Result: ✅ PASS")
except Exception as e:
    print(f"  Result: ❌ FAIL - {type(e).__name__}: {e}")
print()

# Test 4: Unicode content in file (WORKS)
print("TEST 4: Unicode Content in File (ASCII filename)")
print("-" * 40)
try:
    # Create file with Unicode content
    with open("_test_content.txt", "w") as f:
        f.write("café ☕ 日本語 émoji 🎉")
    
    # Read it back
    with open("_test_content.txt", "r") as f:
        content = f.read()
    print(f"  Written: café ☕ 日本語 émoji 🎉")
    print(f"  Read:    {content}")
    
    # Clean up
    os.remove("_test_content.txt")
    
    if content == "café ☕ 日本語 émoji 🎉":
        print("  Result: ✅ PASS")
    else:
        print("  Result: ⚠️ PARTIAL - Content mismatch")
except Exception as e:
    print(f"  Result: ❌ FAIL - {type(e).__name__}: {e}")
print()

# Test 5: Unicode filename - stat (FAILS on Windows)
print("TEST 5: Unicode Filename - os.stat()")
print("-" * 40)
test_names = [
    "café.txt",
    "José_García.txt",
    "日本語.txt",
    "Привет.txt",
]
for name in test_names:
    print(f"  Testing: {name}")
    try:
        # First create the file (this will also fail on Windows)
        with open(name, "w") as f:
            f.write("test")
        st = os.stat(name)
        os.remove(name)
        print(f"    os.stat(): ✅ PASS")
    except UnicodeError as e:
        print(f"    os.stat(): ❌ UnicodeError")
    except OSError as e:
        print(f"    os.stat(): ❌ OSError: {e}")
    except Exception as e:
        print(f"    os.stat(): ❌ {type(e).__name__}: {e}")
print()

# Test 6: Unicode directory name (FAILS on Windows)
print("TEST 6: Unicode Directory - os.mkdir()")
print("-" * 40)
test_dirs = [
    "tëst_dïr",
    "日本語フォルダ",
    "Папка",
]
for name in test_dirs:
    print(f"  Testing: {name}")
    try:
        os.mkdir(name)
        os.rmdir(name)
        print(f"    os.mkdir(): ✅ PASS")
    except UnicodeError as e:
        print(f"    os.mkdir(): ❌ UnicodeError")
    except OSError as e:
        print(f"    os.mkdir(): ❌ OSError: {e}")
    except Exception as e:
        print(f"    os.mkdir(): ❌ {type(e).__name__}: {e}")
print()

print("=" * 60)

