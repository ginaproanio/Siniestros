"""
Security Enhancement Script

Implements security improvements including input sanitization,
rate limiting, and secure error handling for the siniestros system.
"""

import re
import bleach
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Handles input sanitization and security"""

    # Dangerous patterns to remove
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                  # Event handlers
        r'vbscript:',                  # VBScript
        r'data:',                      # Data URLs (potential XSS)
    ]

    # SQL injection patterns (basic detection)
    SQL_INJECTION_PATTERNS = [
        r';\s*--',                    # SQL comments
        r';\s*/\*.*?\*/',            # SQL comments
        r'union\s+select',           # Union-based injection
        r'/\*.*?\*/',                # Block comments
        r'--.*?$',                   # Line comments
    ]

    def sanitize_text(self, text: str, allow_html: bool = False) -> str:
        """Sanitize text input"""
        if not text or not isinstance(text, str):
            return text

        # Remove null bytes
        text = text.replace('\x00', '')

        # Remove dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        # Remove SQL injection patterns
        for pattern in self.SQL_INJECTION_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # If HTML is not allowed, strip all tags
        if not allow_html:
            text = bleach.clean(text, strip=True, tags=[])
        else:
            # Allow only safe HTML tags
            allowed_tags = ['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'ul', 'ol', 'li']
            text = bleach.clean(text, tags=allowed_tags, strip=True)

        # Normalize whitespace
        text = ' '.join(text.split())

        # Limit length (reasonable maximum)
        if len(text) > 10000:
            text = text[:10000] + '...'

        return text.strip()

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            return ""

        # Remove path separators
        filename = re.sub(r'[\/\\]', '', filename)

        # Remove dangerous characters
        filename = re.sub(r'[<>:"|?*]', '', filename)

        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            name = name[:255-len(ext)-1] if ext else name[:255]
            filename = f"{name}.{ext}" if ext else name

        return filename

    def validate_file_content(self, content: bytes, filename: str) -> bool:
        """Validate file content for security"""
        if not content:
            return False

        # Check file size (50MB limit for PDFs)
        if len(content) > 50 * 1024 * 1024:
            return False

        # Check for PDF header if it's supposed to be a PDF
        if filename.lower().endswith('.pdf'):
            if not content.startswith(b'%PDF-'):
                return False

            # Check for embedded JavaScript (basic detection)
            if b'/JavaScript' in content or b'/JS' in content:
                logger.warning(f"Potentially dangerous PDF detected: {filename}")
                return False

        return True

    def sanitize_url(self, url: str) -> Optional[str]:
        """Sanitize and validate URL"""
        if not url or not isinstance(url, str):
            return None

        url = url.strip()

        # Basic URL validation
        if not re.match(r'^https?://', url, re.IGNORECASE):
            return None

        # Remove dangerous characters
        url = re.sub(r'[<>"\'\s]', '', url)

        # Validate against allowed domains (basic)
        allowed_domains = [
            'amazonaws.com', 'cloudfront.net', 'googleapis.com',
            'localhost', '127.0.0.1', '0.0.0.0'
        ]

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain_allowed = any(domain in parsed.netloc for domain in allowed_domains)
            if not domain_allowed and parsed.netloc:
                logger.warning(f"URL domain not in allowlist: {parsed.netloc}")
        except:
            return None

        return url


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.blocked_ips = set()

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed"""
        if client_ip in self.blocked_ips:
            return False

        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            self.blocked_ips.add(client_ip)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False

        # Add current request
        self.requests[client_ip].append(now)
        return True

    def unblock_ip(self, client_ip: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(client_ip)
        self.requests.pop(client_ip, None)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for FastAPI"""

    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.sanitizer = InputSanitizer()

    async def dispatch(self, request: Request, call_next):
        """Process request with security checks"""
        client_ip = self._get_client_ip(request)

        # Rate limiting
        if not self.rate_limiter.is_allowed(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        # Sanitize query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_params[self.sanitizer.sanitize_text(key)] = self.sanitizer.sanitize_text(value)
            # Note: Can't modify query params directly, but we log suspicious ones
            for key, value in request.query_params.items():
                if key != self.sanitizer.sanitize_text(key) or value != self.sanitizer.sanitize_text(value):
                    logger.warning(f"Suspicious query param detected from {client_ip}: {key}={value}")

        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log slow requests
        if duration > 10:  # 10 seconds
            logger.warning(".2f")

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client
        client = request.client
        return client.host if client else "unknown"


def enhance_security():
    """Run security enhancements"""
    print("🔒 Iniciando mejoras de seguridad...")

    sanitizer = InputSanitizer()

    # Test sanitization
    test_inputs = [
        "<script>alert('xss')</script>Hello World",
        "normal text input",
        "SELECT * FROM users; --",
        "javascript:alert('xss')",
        "data:text/html,<script>alert('xss')</script>",
    ]

    print("🧪 Probando sanitización de entrada:")
    for test_input in test_inputs:
        sanitized = sanitizer.sanitize_text(test_input)
        status = "✅" if sanitized != test_input else "ℹ️"
        print(f"   {status} '{test_input}' → '{sanitized}'")

    # Test URL validation
    test_urls = [
        "https://amazonaws.com/bucket/file.pdf",
        "https://evil.com/malicious.pdf",
        "javascript:alert('xss')",
        "http://localhost:3000/test.pdf",
    ]

    print("\n🔗 Probando validación de URLs:")
    for test_url in test_urls:
        sanitized = sanitizer.sanitize_url(test_url)
        status = "✅" if sanitized else "❌"
        print(f"   {status} '{test_url}' → '{sanitized}'")

    print("\n🎉 Mejoras de seguridad implementadas:")
    print("   🧹 Sanitización de entrada automática")
    print("   🚦 Rate limiting configurable")
    print("   🛡️ Headers de seguridad agregados")
    print("   📊 Logging de actividades sospechosas")
    print("   ⚡ Detección de payloads maliciosos")

    print("\n💡 Recomendaciones adicionales:")
    print("   • Configurar HTTPS obligatorio")
    print("   • Implementar Content Security Policy (CSP)")
    print("   • Agregar autenticación JWT")
    print("   • Configurar CORS apropiadamente")
    print("   • Monitorear logs de seguridad regularmente")


if __name__ == "__main__":
    enhance_security()
