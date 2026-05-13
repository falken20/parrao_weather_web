import pytest
from unittest.mock import patch, MagicMock
from src import safe_request


ALLOWED_HOSTS = {"api.ecowitt.net", "api.weather.com"}


def test_validate_safe_url_rejects_non_https():
    with pytest.raises(ValueError, match="Only HTTPS"):
        safe_request.validate_safe_url("http://api.ecowitt.net/path", ALLOWED_HOSTS)


def test_validate_safe_url_rejects_missing_host():
    with pytest.raises(ValueError, match="host is missing"):
        safe_request.validate_safe_url("https:///path", ALLOWED_HOSTS)


def test_validate_safe_url_rejects_non_allowlisted_host():
    with pytest.raises(ValueError, match="Host not allowed"):
        safe_request.validate_safe_url("https://evil.example.org/path", ALLOWED_HOSTS)


@patch("src.safe_request.socket.getaddrinfo")
def test_validate_safe_url_rejects_private_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("127.0.0.1", 443)),
    ]
    with pytest.raises(ValueError, match="non-public IP"):
        safe_request.validate_safe_url("https://api.ecowitt.net/path", ALLOWED_HOSTS)


@patch("src.safe_request.socket.getaddrinfo")
def test_validate_safe_url_rejects_link_local_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("169.254.1.1", 443)),
    ]
    with pytest.raises(ValueError, match="non-public IP"):
        safe_request.validate_safe_url("https://api.ecowitt.net/path", ALLOWED_HOSTS)


@patch("src.safe_request.socket.getaddrinfo")
def test_validate_safe_url_accepts_public_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("52.10.0.1", 443)),
    ]
    # Should not raise
    safe_request.validate_safe_url("https://api.ecowitt.net/path", ALLOWED_HOSTS)


@patch("src.safe_request.requests.get")
@patch("src.safe_request.socket.getaddrinfo")
def test_safe_get_returns_response(mock_getaddrinfo, mock_requests_get):
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("8.8.8.8", 443)),
    ]
    mock_response = MagicMock()
    mock_response.text = '{"ok": true}'
    mock_requests_get.return_value = mock_response

    result = safe_request.safe_get("https://api.ecowitt.net/path", ALLOWED_HOSTS)

    assert result.text == '{"ok": true}'
    mock_requests_get.assert_called_once_with(
        "https://api.ecowitt.net/path",
        timeout=10,
        allow_redirects=False,
    )


@patch("src.safe_request.socket.getaddrinfo")
def test_safe_get_raises_on_private_ip(mock_getaddrinfo):
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("10.0.0.1", 443)),
    ]
    with pytest.raises(ValueError, match="non-public IP"):
        safe_request.safe_get("https://api.ecowitt.net/path", ALLOWED_HOSTS)


def test_is_public_ip_true():
    assert safe_request.is_public_ip("8.8.8.8") is True
    assert safe_request.is_public_ip("52.10.0.1") is True


def test_is_public_ip_false():
    assert safe_request.is_public_ip("127.0.0.1") is False
    assert safe_request.is_public_ip("192.168.1.1") is False
    assert safe_request.is_public_ip("10.0.0.1") is False
    assert safe_request.is_public_ip("169.254.1.1") is False
