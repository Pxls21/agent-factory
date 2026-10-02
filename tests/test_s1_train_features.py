"""tests/test_s1_train_features.py — the on-disk form of the S1 features (scripts/s1_train/features.py; task #441).

Normal: a round trip keeps every value and key; the same arrays give byte-identical files. Failure: a changed byte, a
non-finite value (written or planted), a short file, unsorted or repeated keys, a wrong vector length, a missing or extra
array, a wrong index version or entry, and an output that is not empty are each refused with their reason. Security
boundary (AF-AP-261): an output named with a '..' part is refused before anything is created, so a missing part before
the '..' cannot redirect the write into a full directory.
"""
import array
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from s1_train import features as F  # noqa: E402

DIM = 3


def arrays_for(rows, free, shift=0.0):
    """Exactly representable float32 values (multiples of 1/8), distinct per array, row and column."""
    out = {}
    for n, name in enumerate(F.ROW_ARRAYS + F.FREE_ARRAYS):
        keys = rows if name in F.ROW_ARRAYS else free
        out[name] = [[shift + n + i / 8.0 + j / 64.0 for j in range(DIM)] for i in range(len(keys))]
    return out


ROWS = ["s1-0001", "s1-0002", "s1-0003"]
FREE = ["aa" * 32, "bb" * 32]
META = {"backend": {"name": "test"}, "counts": {"rows": 3}}


def write(tmp_path, name="out", **kw):
    args = dict(rows=ROWS, free=FREE, dim=DIM, arrays=arrays_for(ROWS, FREE), meta=META)
    args.update(kw)
    return F.write(str(tmp_path / name), **args)


def reseal(d, name, data):
    """Plant `data` as an array file and make the index's sha256 agree, so only the check under test can refuse it."""
    (d / (name + ".f32")).write_bytes(data)
    idx = json.loads((d / F.INDEX).read_text())
    idx["arrays"][name]["sha256"] = hashlib.sha256(data).hexdigest()
    (d / F.INDEX).write_text(json.dumps(idx))


def test_round_trip_keeps_every_value_and_key(tmp_path):
    write(tmp_path)
    index, m = F.read(str(tmp_path / "out"))
    assert index["version"] == F.VERSION and index["dim"] == DIM and index["meta"] == META
    want = arrays_for(ROWS, FREE)
    for name in F.ROW_ARRAYS + F.FREE_ARRAYS:
        keys = ROWS if name in F.ROW_ARRAYS else FREE
        assert m[name].keys == keys
        assert [m[name].row(i) for i in range(len(keys))] == want[name]
    assert m["c_ctx"].get("s1-0002") == want["c_ctx"][1]
    assert m["q_free"].get(FREE[1]) == want["q_free"][1]


def test_same_arrays_give_byte_identical_files(tmp_path):
    write(tmp_path, "a")
    write(tmp_path, "b")
    names = sorted(os.listdir(tmp_path / "a"))
    assert names == sorted([F.INDEX] + [n + ".f32" for n in F.ROW_ARRAYS + F.FREE_ARRAYS])
    for n in names:
        assert (tmp_path / "a" / n).read_bytes() == (tmp_path / "b" / n).read_bytes(), n


def test_a_changed_byte_is_refused(tmp_path):
    write(tmp_path)
    p = tmp_path / "out" / "q_ctx.f32"
    b = bytearray(p.read_bytes())
    b[5] ^= 1
    p.write_bytes(bytes(b))
    with pytest.raises(F.Refused, match="q_ctx: the file's sha256 is not the index's"):
        F.read(str(tmp_path / "out"))


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_a_non_finite_value_is_refused_at_write(tmp_path, bad):
    arrs = arrays_for(ROWS, FREE)
    arrs["s_w"][2][1] = bad
    with pytest.raises(F.Refused, match="s_w: a value is not finite"):
        write(tmp_path, arrays=arrs)
    assert not (tmp_path / "out").exists()


def test_a_planted_nan_is_refused_at_read(tmp_path):
    write(tmp_path)
    a = array.array("f", [0.5] * (DIM * len(FREE)))
    a[4] = math.nan
    if sys.byteorder != "little":
        a.byteswap()
    reseal(tmp_path / "out", "c_free", a.tobytes())
    with pytest.raises(F.Refused, match="c_free: a value is not finite"):
        F.read(str(tmp_path / "out"))


def test_a_short_file_is_refused(tmp_path):
    write(tmp_path)
    d = tmp_path / "out"
    reseal(d, "s", (d / "s.f32").read_bytes()[:-4])
    with pytest.raises(F.Refused, match="s: 32 bytes, not 36"):
        F.read(str(d))


@pytest.mark.parametrize("rows,why", [(["s1-0002", "s1-0001", "s1-0003"], "sorted and distinct"),
                                      (["s1-0001", "s1-0001", "s1-0003"], "sorted and distinct"),
                                      (["s1-0001", "", "s1-0003"], "a list of non-empty strings")])
def test_bad_keys_are_refused(tmp_path, rows, why):
    with pytest.raises(F.Refused, match="rows: the keys must be " + why):
        write(tmp_path, rows=rows)


def test_a_wrong_vector_length_or_count_is_refused(tmp_path):
    arrs = arrays_for(ROWS, FREE)
    arrs["c_ctx"][1] = arrs["c_ctx"][1][:2]
    with pytest.raises(F.Refused, match=r"c_ctx\[1\]: 2 values, not 3"):
        write(tmp_path, arrays=arrs)
    arrs = arrays_for(ROWS, FREE)
    arrs["q_free"] = arrs["q_free"][:1]
    with pytest.raises(F.Refused, match="q_free: 1 vectors for 2 keys"):
        write(tmp_path, arrays=arrs)


def test_a_missing_or_extra_array_is_refused(tmp_path):
    arrs = arrays_for(ROWS, FREE)
    del arrs["s_w"]
    with pytest.raises(F.Refused, match="arrays must be exactly"):
        write(tmp_path, arrays=arrs)
    arrs = arrays_for(ROWS, FREE)
    arrs["extra"] = arrs["s"]
    with pytest.raises(F.Refused, match="arrays must be exactly"):
        write(tmp_path, arrays=arrs)


def test_a_wrong_index_is_refused(tmp_path):
    write(tmp_path)
    d = tmp_path / "out"
    idx = json.loads((d / F.INDEX).read_text())
    idx["version"] = "s1-features-v0"
    (d / F.INDEX).write_text(json.dumps(idx))
    with pytest.raises(F.Refused, match="not a s1-features-v1 index"):
        F.read(str(d))
    idx["version"] = F.VERSION
    idx["arrays"]["c_free"]["keys"] = "rows"
    (d / F.INDEX).write_text(json.dumps(idx))
    with pytest.raises(F.Refused, match="c_free: the index entry is not"):
        F.read(str(d))
    (d / F.INDEX).unlink()
    with pytest.raises(F.Refused, match="no readable index.json"):
        F.read(str(d))


def test_an_output_that_is_not_empty_or_is_a_link_is_refused(tmp_path):
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "keep.txt").write_text("keep\n")
    with pytest.raises(F.Refused, match="must not exist, or be an empty directory"):
        write(tmp_path, "full")
    (tmp_path / "empty").mkdir()
    os.symlink(tmp_path / "empty", tmp_path / "link")
    with pytest.raises(F.Refused, match="must not exist, or be an empty directory"):
        write(tmp_path, "link")
    assert os.listdir(tmp_path / "empty") == []
    write(tmp_path, "empty")                          # an empty directory is taken
    assert F.read(str(tmp_path / "empty"))[0]["rows"] == ROWS


def test_a_dotdot_output_is_refused_before_anything_is_made(tmp_path):
    """AF-AP-261: <tmp>/missing/../full names <tmp>/full once makedirs has made <tmp>/missing; the text checks would
    see a path that does not exist and pass it."""
    (tmp_path / "full").mkdir()
    (tmp_path / "full" / "s.f32").write_text("OLDER OUTPUT\n")
    for spelling in (str(tmp_path / "missing") + "/../full", str(tmp_path / "missing") + "/..", ".."):
        with pytest.raises(F.Refused, match="without a '..' part"):
            F.write(spelling, rows=ROWS, free=FREE, dim=DIM, arrays=arrays_for(ROWS, FREE), meta=META)
    assert not (tmp_path / "missing").exists()
    assert (tmp_path / "full" / "s.f32").read_text() == "OLDER OUTPUT\n"
    with pytest.raises(F.Refused, match="without a '..' part"):
        F.write("", rows=ROWS, free=FREE, dim=DIM, arrays=arrays_for(ROWS, FREE), meta=META)
