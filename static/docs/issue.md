# Issue List

## An Error in tree-sitter Installation

After executing `cd lib && python build.py`, I encountered the following error message:

```
/Users/guest/Code/RepoAudit/lib/vendor/tree-sitter-cpp/src/scanner.c:126:5: error: call to undeclared function 'static_assert'; ISO C99 and later do not support implicit function declarations [-Wimplicit-function-declaration]
    static_assert(MAX_DELIMITER_LENGTH * sizeof(wchar_t) < TREE_SITTER_SERIALIZATION_BUFFER_SIZE,
    ^
1 error generated.
Traceback (most recent call last):
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/distutils/unixccompiler.py", line 118, in _compile
    self.spawn(compiler_so + cc_args + [src, '-o', obj] +
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/distutils/ccompiler.py", line 910, in spawn
    spawn(cmd, dry_run=self.dry_run)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/distutils/spawn.py", line 91, in spawn
    raise DistutilsExecError(
distutils.errors.DistutilsExecError: command '/usr/bin/cc' failed with exit code 1

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/guest/Code/RepoAudit/lib/build.py", line 34, in <module>
    Language.build_library(
  File "/Users/guest/Library/Python/3.9/lib/python/site-packages/tree_sitter/__init__.py", line 85, in build_library
    compiler.compile(
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/distutils/ccompiler.py", line 574, in compile
    self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
  File "/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/distutils/unixccompiler.py", line 121, in _compile
    raise CompileError(msg)
distutils.errors.CompileError: command '/usr/bin/cc' failed with exit code 1
```

**Solution**: Open the file `/Users/guest/Code/RepoAudit/lib/vendor/tree-sitter-cpp/src/scanner.c` and comment the `static_assert` statement in the following function:

```
unsigned tree_sitter_cpp_external_scanner_serialize(void *payload, char *buffer) {
    // static_assert(MAX_DELIMITER_LENGTH * sizeof(wchar_t) < TREE_SITTER_SERIALIZATION_BUFFER_SIZE,
    //              "Serialized delimiter is too long!");

    Scanner *scanner = (Scanner *)payload;
    size_t size = scanner->delimiter_length * sizeof(wchar_t);
    memcpy(buffer, scanner->delimiter, size);
    return (unsigned)size;
}
```

Then you can execute `cd lib && python build.py` again for installation.