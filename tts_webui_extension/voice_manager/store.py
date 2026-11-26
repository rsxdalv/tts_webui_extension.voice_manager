"""Filesystem helpers for the Voice Manager (no Gradio imports, so they can be tested)."""

import os
import shutil
from datetime import datetime

AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".opus"}
ROOT_LABEL = "(root)"


def voices_dir() -> str:
    """Folder that holds the voices: $TTS_WEBUI_VOICES_DIR, else ./voices (the app runs from its root)."""
    path = os.environ.get("TTS_WEBUI_VOICES_DIR") or os.path.join(os.getcwd(), "voices")
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    return path


def _inside(base: str, target: str) -> bool:
    base, target = os.path.realpath(base), os.path.realpath(target)
    return os.path.commonpath([base, target]) == base


def valid_name(name: str) -> bool:
    """One plain path element: no separators, no '.'/'..', no leading dot."""
    return (
        bool(name)
        and name == name.strip()
        and name not in (".", "..")
        and not name.startswith(".")
        and "/" not in name
        and "\\" not in name
        and "\x00" not in name
        and os.path.basename(name) == name
    )


def resolve_subdir(subdir: str | None) -> str:
    base = voices_dir()
    if not subdir or subdir == ROOT_LABEL:
        return base
    if not valid_name(subdir):
        raise ValueError("Invalid subdirectory")
    target = os.path.join(base, subdir)
    if not _inside(base, target):
        raise ValueError("Invalid subdirectory")
    return target


def list_subdirs() -> list[str]:
    base = voices_dir()
    names = [
        e for e in sorted(os.listdir(base)) if os.path.isdir(os.path.join(base, e))
    ]
    return [ROOT_LABEL, *names]


def human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def list_files(subdir: str | None) -> list[list[str]]:
    target = resolve_subdir(subdir)
    if not os.path.isdir(target):
        return []
    rows = []
    for fname in sorted(os.listdir(target)):
        fpath = os.path.join(target, fname)
        if not os.path.isfile(fpath):
            continue
        if os.path.splitext(fname)[1].lower() not in AUDIO_EXTENSIONS:
            continue
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime(
            "%Y-%m-%d %H:%M"
        )
        rows.append([fname, human_size(os.path.getsize(fpath)), mtime])
    return rows


def _unique_path(target: str, fname: str) -> str:
    stem, ext = os.path.splitext(fname)
    dest, n = os.path.join(target, fname), 1
    while os.path.exists(dest):
        dest = os.path.join(target, f"{stem}_{n}{ext}")
        n += 1
    return dest


def add_files(paths: list[str], subdir: str | None) -> tuple[int, list[str]]:
    """Copy files into the folder. Existing names are kept (a numeric suffix is added)."""
    target = resolve_subdir(subdir)
    os.makedirs(target, exist_ok=True)
    count, skipped = 0, []
    for src in paths:
        fname = os.path.basename(src)
        if (
            not valid_name(fname)
            or os.path.splitext(fname)[1].lower() not in AUDIO_EXTENSIONS
        ):
            skipped.append(fname)
            continue
        shutil.copy2(src, _unique_path(target, fname))
        count += 1
    return count, skipped


def remove_file(subdir: str | None, fname: str) -> bool:
    target = resolve_subdir(subdir)
    if (
        not valid_name(fname)
        or os.path.splitext(fname)[1].lower() not in AUDIO_EXTENSIONS
    ):
        raise ValueError("Invalid file name")
    fpath = os.path.join(target, fname)
    if not _inside(target, fpath) or os.path.islink(fpath) or not os.path.isfile(fpath):
        return False
    os.remove(fpath)
    return True


def make_subdir(name: str) -> str:
    name = (name or "").strip()
    if not valid_name(name):
        raise ValueError("Invalid directory name.")
    target = os.path.join(voices_dir(), name)
    if os.path.exists(target):
        raise FileExistsError(f"Directory '{name}' already exists.")
    os.makedirs(target)
    return name
