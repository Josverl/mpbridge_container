# mpbridge/ConPTY Unicode Encoding Issue

## Summary

Unicode file operations fail when using mpbridge on Windows, but work correctly when running MicroPython directly. The issue is in the ConPTY/pywinpty encoding chain, not MicroPython.

**MicroPython Windows handles Unicode correctly:**
- ✅ Unicode filenames work
- ✅ Unicode content in files works
- ✅ Unicode string operations work
- ✅ Unicode console output works

## Evidence

### Direct MicroPython Windows (ALL PASS ✅)

Running the test script directly in MicroPython Windows:

```
>>> import test_unicode_filenames
============================================================
MicroPython Windows Unicode Filename Test
============================================================
Platform: win32

TEST 1: Unicode Console Output
  Result: ✅ PASS

TEST 2: Unicode String Operations
  String: Adéọlá_Olúwadáre
  Length: 16
  Result: ✅ PASS

TEST 3: ASCII Filename Operations
  Result: ✅ PASS

TEST 4: Unicode Content in File (ASCII filename)
  Result: ✅ PASS

TEST 5: Unicode Filename - os.stat()
  café.txt: ✅ PASS
  José_García.txt: ✅ PASS
  日本語.txt: ✅ PASS
  Привет.txt: ✅ PASS

TEST 6: Unicode Directory - os.mkdir()
  tëst_dïr: ✅ PASS
  日本語フォルダ: ✅ PASS
  Папка: ✅ PASS
```

Note: Console displays garbled characters (`caf├⌐` instead of `café`) because Windows console interprets UTF-8 bytes using CP437/CP850 code page. The actual data is correct.

### Via mpbridge (TESTS FAIL ❌)

```
mpremote connect socket://localhost:2218 run test_unicode_filenames.py
============================================================
MicroPython Windows Unicode Filename Test
============================================================
Platform: win32

TEST 2: Unicode String Operations
  String: Adé?lá_Olúwadáre
  Length: 12  ← should be 16, bytes are corrupted
  Result: ✅ PASS  ← false positive

TEST 4: Unicode Content in File (ASCII filename)
  Result: ❌ FAIL - UnicodeError

TEST 5: Unicode Filename - os.stat()
  café.txt: ❌ UnicodeError
  José_García.txt: ❌ UnicodeError
  ???.txt: ❌ OSError: [Errno 22] EINVAL
```

## Root Cause: ConPTY Encoding Chain

The corruption happens in the mpbridge → pywinpty → ConPTY → MicroPython path:

1. **mpremote sends UTF-8** → mpbridge receives correct bytes
2. **mpbridge writes to pywinpty** → `pty.write(text)` 
3. **ConPTY** → transforms encoding (code page instead of UTF-8?)
4. **MicroPython receives** → corrupted bytes
5. **MicroPython outputs UTF-8** → valid bytes
6. **ConPTY** → decodes with wrong code page
7. **pywinpty.read()** → corrupted string
8. **mpbridge** → corrupted bytes sent to mpremote

## mpbridge Debug Log

mpbridge transmits correct UTF-8 bytes:

```
Write 76 bytes: b"print(repr(os.stat('foo_bar/test_data/African/Ad\xc3\xa9\xe1\xbb\x8dl\xc3\xa1_Ol\xc3\xbawad\xc3\xa1re.txt')))"
```

The bytes `\xc3\xa9` = `é`, `\xe1\xbb\x8d` = `ọ` are correct UTF-8. Corruption happens in ConPTY.

## Recommended Fix for mpbridge

Configure pywinpty/ConPTY for UTF-8:

1. **Set console code page to UTF-8 before spawning:**
   ```python
   import ctypes
   ctypes.windll.kernel32.SetConsoleCP(65001)        # Input
   ctypes.windll.kernel32.SetConsoleOutputCP(65001)  # Output
   ```

2. **Use environment variables in spawn():**
   ```python
   env_dict["PYTHONIOENCODING"] = "utf-8"
   ```

3. **Investigate pywinpty's internal encoding handling** - may need to pass raw bytes instead of strings

## Next Steps

1. **Enable ConPTY UTF-8 mode** - Windows 10+ may have UTF-8 support that needs activation
2. **Check pywinpty configuration** - May need to configure encoding at spawn time
3. **Consider raw byte mode** - Alternative if ConPTY cannot handle UTF-8 properly

## Test Files

Test data in `unicode_mpy/test_data/` with filenames in various scripts:
- Latin/Western European: `José_García.txt`, `François_Müller.txt`
- East Asian: `田中太郎_山田花子.txt`, `さくら_はな.txt`
- Cyrillic: Russian, Ukrainian names
- African: `Adéọlá_Olúwadáre.txt` (Yoruba with dot-below)
