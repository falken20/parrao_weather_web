# by Richi Rod AKA @richionline / falken20
#
# Módulo reutilizable de protección DNS/SSRF para peticiones HTTP salientes.
# Úsalo en cualquier proyecto importando validate_safe_url y safe_get.

import socket
import ipaddress
from urllib.parse import urlparse

import requests


def is_public_ip(ip_str: str) -> bool:
    """Return True only for routable public IPs (not private, loopback, etc.)."""
    ip_obj = ipaddress.ip_address(ip_str)
    return not (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_multicast
        or ip_obj.is_reserved
        or ip_obj.is_unspecified
    )


def validate_safe_url(url: str, allowed_hosts: set):
    """Validate that a URL is safe to request.

    Checks:
      - Scheme is HTTPS.
      - Host is in the allowed_hosts set.
      - All DNS-resolved IPs are public (not private/loopback/link-local).

    Args:
        url: The full URL to validate.
        allowed_hosts: A set of permitted hostnames (e.g. {"api.example.com"}).

    Raises:
        ValueError: If any validation check fails.
    """
    parsed_url = urlparse(url)

    if parsed_url.scheme.lower() != "https":
        raise ValueError("Only HTTPS URLs are allowed")

    host = parsed_url.hostname
    if not host:
        raise ValueError("URL host is missing")

    if host not in allowed_hosts:
        raise ValueError(f"Host not allowed: {host}")

    # Check all DNS answers to reduce DNS rebinding/poisoning impact.
    resolved_ips = {
        addr_info[4][0]
        for addr_info in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    }
    if not resolved_ips:
        raise ValueError(f"No DNS records found for host: {host}")

    for ip in resolved_ips:
        if not is_public_ip(ip):
            raise ValueError(f"Host resolves to non-public IP: {ip}")


def safe_get(url: str, allowed_hosts: set, timeout: int = 10) -> requests.Response:
    """Perform a validated GET request with DNS/SSRF protections.

    Args:
        url: The full URL to fetch.
        allowed_hosts: Set of permitted hostnames.
        timeout: Request timeout in seconds (default 10).

    Returns:
        requests.Response object.

    Raises:
        ValueError: If the URL fails safety validation.
        requests.RequestException: On network/HTTP errors.
    """
    validate_safe_url(url, allowed_hosts)
    return requests.get(url, timeout=timeout, allow_redirects=False)
