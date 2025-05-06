from app import format_cl_currency

def test_format_cl_currency():
    """Test the Chilean currency formatting function."""
    # Test con diferentes valores
    assert format_cl_currency(1000) == "$1.000"
    assert format_cl_currency(1000000) == "$1.000.000"
    assert format_cl_currency(1500) == "$1.500"
    assert format_cl_currency(0) == "$0"