import sys
import os
import builtins
import importlib.abc
import importlib.util
from io import BytesIO
import struct
import zlib
import tempfile
import atexit

# =========================
# CONFIG
# =========================
BUNDLE_PATH = "assets.bin" # None = auto-detect (appended to exe)

def vfs_log(func_name, params, action):
    print(f"[VFS]({func_name}, {params}) {action}")

# =========================
# VFS CORE
# =========================
class VFS:
    MAGIC = b"RCPT"

    def __init__(self):
        self.index = {}
        self.fp = None
        self._load_bundle()

    def _load_bundle(self):
        path = BUNDLE_PATH or sys.executable
        print(f"{BUNDLE_PATH=}")
        vfs_log("_load_bundle", f"path={path}", "loading bundle")
        with open(path, "rb") as f:
            data = f.read()

        pos = data.rfind(self.MAGIC)
        if pos == -1:
            vfs_log("_load_bundle", f"path={path}", "no bundle found")
            return

        self.fp = data
        offset = pos + len(self.MAGIC)
        count = struct.unpack_from("<I", data, offset)[0]
        offset += 4

        for _ in range(count):
            path_len = struct.unpack_from("<H", data, offset)[0]
            offset += 2

            path_bytes = data[offset:offset + path_len]
            offset += path_len
            path_str = path_bytes.decode()

            file_offset, file_size = struct.unpack_from("<II", data, offset)
            offset += 8

            self.index[path_str] = (file_offset, file_size)
        vfs_log("_load_bundle", f"loaded {len(self.index)} files", "bundle loaded")

    def exists(self, path: str) -> bool:
        path = path.rstrip("/").replace("\\", "/")
        if path in self.index:
            vfs_log("exists", f"path={path}", "file exists")
            return True

        # check if any file starts with this path + "/"
        for p in self.index:
            if p.startswith(path + "/"):
                vfs_log("exists", f"path={path}", "directory exists")
                return True

        vfs_log("exists", f"path={path}", "does not exist")
        return False

    def read(self, path: str) -> bytes:
        path = path.replace("\\", "/")
        if path not in self.index:
            vfs_log("read", f"path={path}", "file not found")
            raise FileNotFoundError(path)

        off, size = self.index[path]
        raw = self.fp[off:off + size]

        try:
            data = zlib.decompress(raw)
            vfs_log("read", f"path={path}", f"read {len(data)} bytes (decompressed)")
            return data
        except:
            vfs_log("read", f"path={path}", f"read {len(raw)} bytes (raw)")
            return raw

    def open_file(self, path: str):
        vfs_log("open_file", f"path={path}", "returning BytesIO")
        return BytesIO(self.read(path))

    def listdir(self, path: str):
        # map "." to root
        path = path.rstrip("/").replace("\\", "/")
        if path == ".":
            path = ""
        out = set()

        for p in self.index:
            if path:
                if not p.startswith(path + "/"):
                    continue
                rest = p[len(path)+1:]  # skip prefix + /
            else:
                rest = p

            if rest:
                out.add(rest.split("/")[0])

        vfs_log("listdir", f"path={path}", f"found {len(out)} entries")
        return list(out)


vfs = VFS()

# =========================
# PATCH OPEN / OS
# =========================
_real_open = builtins.open
_real_exists = os.path.exists
_real_listdir = os.listdir

def vfs_tree(path: str = ".", prefix: str = "") -> None:
    """
    Print a tree of the VFS starting from 'path'.
    """
    # map "." to root of VFS
    if path == ".":
        path = ""

    if not vfs.exists(path):
        print(f"{prefix}{path or '.'} [not found]")
        return

    entries = vfs.listdir(path)
    entries.sort()
    for i, entry in enumerate(entries):
        full_path = f"{path}/{entry}" if path else entry
        connector = "└── " if i == len(entries) - 1 else "├── "
        print(f"{prefix}{connector}{entry}")
        # Recurse if entry is a directory
        if vfs.exists(full_path) and vfs.listdir(full_path):
            extension = "    " if i == len(entries) - 1 else "│   "
            vfs_tree(full_path, prefix + extension)

def vfs_open(path, *args, **kwargs):
    if isinstance(path, str) and vfs.exists(path):
        vfs_log("vfs_open", f"path={path}", "serving from VFS")
        return vfs.open_file(path)
    vfs_log("vfs_open", f"path={path}", "fallback to real open")
    return _real_open(path, *args, **kwargs)

def vfs_exists(path):
    exists = vfs.exists(path) or _real_exists(path)
    vfs_log("vfs_exists", f"path={path}", f"exists={exists}")
    return exists

def vfs_listdir(path):
    if vfs.exists(path):
        vfs_log("vfs_listdir", f"path={path}", "listing VFS directory")
        return vfs.listdir(path)
    vfs_log("vfs_listdir", f"path={path}", "fallback to real listdir")
    return _real_listdir(path)

builtins.open = vfs_open
exists = vfs_exists
listdir = vfs_listdir

# =========================
# IMPORT HOOK
# =========================
class VFSLoader(importlib.abc.Loader):
    def create_module(self, spec):
        vfs_log("VFSLoader.create_module", f"module={spec.name}", "creating module")
        return None

    def exec_module(self, module):
        vfs_log("VFSLoader.exec_module", f"module={module.__name__}", "executing module")
        code = vfs.read(module.__spec__.origin)
        exec(compile(code, module.__spec__.origin, "exec"), module.__dict__)

class VFSFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        rel = fullname.replace(".", "/") + ".py"

        if vfs.exists(rel):
            vfs_log("VFSFinder.find_spec", f"module={fullname}", "found module in VFS")
            return importlib.util.spec_from_loader(
                fullname,
                VFSLoader(),
                origin=rel
            )

        # package (__init__.py)
        rel_init = fullname.replace(".", "/") + "/__init__.py"
        if vfs.exists(rel_init):
            vfs_log("VFSFinder.find_spec", f"module={fullname}", "found package in VFS")
            return importlib.util.spec_from_loader(
                fullname,
                VFSLoader(),
                origin=rel_init,
                is_package=True
            )

        vfs_log("VFSFinder.find_spec", f"module={fullname}", "not found in VFS")
        return None

sys.meta_path.insert(0, VFSFinder())

# =========================
# TEMP FILE HANDLER
# =========================
_temp_files = []

def extract_temp(path_in_bundle):
    fp = vfs.read(path_in_bundle)
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(fp)
    tmp.close()
    _temp_files.append(tmp.name)
    vfs_log("extract_temp", f"path={path_in_bundle}", f"extracted to {tmp.name}")
    return tmp.name

def cleanup_temp_files():
    for f in _temp_files:
        try:
            os.unlink(f)
            vfs_log("cleanup_temp_files", f"file={f}", "deleted temp file")
        except:
            pass

atexit.register(cleanup_temp_files)

# =========================
# PATCH cv2.imread
# =========================
try:
    import cv2
    _real_imread = cv2.imread

    def vfs_imread(path, *args, **kwargs):
        if vfs.exists(path):
            tmp_path = extract_temp(path)
            vfs_log("cv2.imread", f"path={path}", f"reading via temp {tmp_path}")
            return _real_imread(tmp_path, *args, **kwargs)
        vfs_log("cv2.imread", f"path={path}", "reading from real path")
        return _real_imread(path, *args, **kwargs)

    imread = vfs_imread
except ImportError:
    vfs_log("cv2.imread patch", "cv2 not installed", "skipped patch")
