"""Contratto portabile delle risorse multimediali locali."""

from pathlib import PurePosixPath, PureWindowsPath

IMAGE_FORMATS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}
AUDIO_FORMATS = {
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".wav": "audio/wav",
}
MEDIA_FORMATS = {**IMAGE_FORMATS, **AUDIO_FORMATS}
MAX_RESOURCE_BYTES = 5_000_000
MAX_PROJECT_RESOURCE_BYTES = 20_000_000
MAX_RESOURCES = 64


def valid_resource_path(path: str) -> bool:
    """Accetta soltanto percorsi POSIX relativi, senza segmenti speciali."""
    return bool(path) and not (
        PurePosixPath(path).is_absolute()
        or PureWindowsPath(path).drive
        or "\\" in path
        or ":" in path
        or "\x00" in path
        or any(character in path for character in "\r\n")
        or any(part in {"", ".", ".."} for part in path.split("/"))
    )


def resource_media_type(kind: str, path: str) -> str:
    """Restituisce il MIME previsto o rifiuta percorso/formato incoerenti."""
    if not valid_resource_path(path):
        raise ValueError("Usa un percorso relativo sicuro con separatori '/'.")
    suffix = PurePosixPath(path).suffix.casefold()
    formats = IMAGE_FORMATS if kind == "immagine" else AUDIO_FORMATS if kind == "suono" else {}
    media_type = formats.get(suffix)
    if media_type is None:
        expected = ", ".join(sorted(formats)) if formats else "nessuno"
        raise ValueError(f"Formato non ammesso per {kind}: usa {expected}.")
    return media_type


def valid_media_content(media_type: str, header: bytes) -> bool:
    """Controlla la firma minima del formato dichiarato, senza decodificarlo."""
    checks = {
        "image/png": header.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": header.startswith(b"\xff\xd8\xff"),
        "image/gif": header.startswith((b"GIF87a", b"GIF89a")),
        "image/webp": len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP",
        "audio/ogg": header.startswith(b"OggS"),
        "audio/wav": len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WAVE",
        "audio/mpeg": header.startswith(b"ID3")
        or (len(header) >= 2 and header[0] == 0xFF and header[1] & 0xE0 == 0xE0),
    }
    return checks.get(media_type, False)
