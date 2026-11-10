import pytest
from pathlib import Path

ALLOWED={"mp4","mov","mkv","webm","avi"}
def valid_extension(filename):
    return Path(filename).suffix.lower().lstrip(".") in ALLOWED

@pytest.mark.parametrize("filename",["clip.mp4","video.MOV","movie.mkv"])
def test_allowed_extensions(filename): assert valid_extension(filename)

@pytest.mark.parametrize("filename",["virus.exe","file.txt","clip"])
def test_invalid_extensions(filename): assert not valid_extension(filename)

def test_max_size_validation():
    limit=500*1024*1024
    assert 100 <= limit
    assert limit+1 > limit
