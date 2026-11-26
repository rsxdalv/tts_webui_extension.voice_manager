import os

import pytest

from tts_webui_extension.voice_manager import store


@pytest.fixture(autouse=True)
def voices(tmp_path, monkeypatch):
    d = tmp_path / "voices"
    monkeypatch.setenv("TTS_WEBUI_VOICES_DIR", str(d))
    return d


def _clip(tmp_path, name="a.wav", data=b"x"):
    p = tmp_path / "src" / name
    p.parent.mkdir(exist_ok=True)
    p.write_bytes(data)
    return str(p)


def test_add_list_remove(tmp_path):
    assert store.add_files([_clip(tmp_path)], "(root)") == (1, [])
    assert [r[0] for r in store.list_files("(root)")] == ["a.wav"]
    assert store.remove_file("(root)", "a.wav") is True
    assert store.list_files("(root)") == []


def test_upload_does_not_overwrite(tmp_path, voices):
    store.add_files([_clip(tmp_path, data=b"one")], "(root)")
    store.add_files([_clip(tmp_path, data=b"two")], "(root)")
    assert sorted(os.listdir(voices)) == ["a.wav", "a_1.wav"]
    assert (voices / "a.wav").read_bytes() == b"one"


def test_unsupported_extension_skipped(tmp_path):
    n, skipped = store.add_files([_clip(tmp_path, "evil.py")], "(root)")
    assert n == 0 and skipped == ["evil.py"]


@pytest.mark.parametrize("bad", ["..", "../x", "a/b", "a\\b", ".hidden", "", "."])
def test_bad_subdir_names_rejected(bad):
    with pytest.raises(ValueError):
        store.make_subdir(bad)
    if bad:
        with pytest.raises(ValueError):
            store.resolve_subdir(bad)


def test_sibling_prefix_dir_not_accepted(tmp_path, voices):
    voices.mkdir()
    (tmp_path / "voices_x").mkdir()
    with pytest.raises(ValueError):
        store.resolve_subdir("../voices_x")


def test_delete_rejects_traversal_and_symlink(tmp_path, voices):
    voices.mkdir()
    outside = tmp_path / "secret.wav"
    outside.write_bytes(b"s")
    (voices / "link.wav").symlink_to(outside)
    with pytest.raises(ValueError):
        store.remove_file("(root)", "../secret.wav")
    assert store.remove_file("(root)", "link.wav") is False
    assert outside.exists()


def test_make_subdir_and_list(tmp_path):
    assert store.make_subdir("mine") == "mine"
    with pytest.raises(FileExistsError):
        store.make_subdir("mine")
    assert store.list_subdirs() == ["(root)", "mine"]
    store.add_files([_clip(tmp_path)], "mine")
    assert len(store.list_files("mine")) == 1
