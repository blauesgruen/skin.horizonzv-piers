"""Wrap the authored audit AVI frames in Matroska with three named chapters.

Usage: python create_chapter_fixture.py input.avi output.mkv
Fixture only, not a general AVI reader or Matroska muxer.
References: https://www.matroska.org/technical/elements.html
https://www.matroska.org/technical/codec_specs.html#v-ms-vfw-fourcc
"""
from pathlib import Path
import struct
import sys


def element(identifier, payload):
    ident = bytes.fromhex(identifier)
    for width in range(1, 9):
        if len(payload) < (1 << (7 * width)) - 1:
            size = ((1 << (7 * width)) | len(payload)).to_bytes(width, "big")
            return ident + size + payload
    raise ValueError("Element too large")


def integer(identifier, value):
    return element(identifier, value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big"))


def create(source, destination):
    avi = source.read_bytes()
    assert avi[:4] == b"RIFF" and avi[8:12] == b"AVI "
    offset = avi.index(b"strf")
    bitmap = avi[offset + 8:offset + 48]
    assert struct.unpack("<IiiHHI", bitmap[:20]) == (40, 160, 90, 1, 24, 0)
    offset = avi.index(b"00db")
    size = struct.unpack("<I", avi[offset + 4:offset + 8])[0]
    frame = avi[offset + 8:offset + 8 + size]
    assert len(frame) == 160 * 90 * 3
    header = element("1A45DFA3", integer("4286", 1) + integer("42F7", 1)
                     + integer("42F2", 4) + integer("42F3", 8)
                     + element("4282", b"matroska") + integer("4287", 4) + integer("4285", 2))
    info = element("1549A966", integer("2AD7B1", 1000000)
                   + element("4489", struct.pack(">d", 90000.0))
                   + element("4D80", b"Skin audit fixture") + element("5741", b"Skin audit fixture"))
    video = element("E0", integer("B0", 160) + integer("BA", 90))
    track = element("AE", integer("D7", 1) + integer("73C5", 1) + integer("83", 1)
                    + element("86", b"V_MS/VFW/FOURCC") + element("63A2", bitmap)
                    + integer("23E383", 200000000) + video)
    chapters = b""
    for number in range(3):
        display = element("80", element("85", f"Audit chapter {number + 1}".encode())
                          + element("437C", b"eng"))
        chapters += element("B6", integer("73C4", number + 1)
                            + integer("91", number * 30000000000)
                            + integer("92", (number + 1) * 30000000000) + display)
    chapters = element("1043A770", element("45B9", chapters))
    clusters = b""
    for start in (0, 30000, 60000):
        blocks = b"".join(element("A3", b"\x81" + struct.pack(">h", frame_no * 200)
                                   + b"\x80" + frame) for frame_no in range(150))
        clusters += element("1F43B675", integer("E7", start) + blocks)
    destination.write_bytes(header + element("18538067", info + element("1654AE6B", track)
                                            + chapters + clusters))


if __name__ == "__main__":
    create(Path(sys.argv[1]), Path(sys.argv[2]))
