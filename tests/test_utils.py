import pytest
from src.utils import format_size

@pytest.mark.parametrize("bytes_value,expected", [
    (0, "0.00B"),
    (1023, "1023.00B"),
    (1024, "1.00KB"),
    (1024 * 1024, "1.00MB"),
    (1024 * 1024 * 1024, "1.00GB"),
    (1024 * 1024 * 1024 * 1024, "1.00TB"),
    (1500, "1.46KB"),
    (1500000, "1.43MB"),
])
def test_format_size(bytes_value, expected):
    assert format_size(bytes_value) == expected 