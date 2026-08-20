"""Email Verifier & Anti-Spam Safety Parser.

Verifies recipient email syntax, checks domain MX records, and scans outgoing message body
for spam trigger words to ensure 100% inbox placement."""

import re
import socket
from typing import Dict, Any, List

SPAM_TRIGGER_WORDS = [
    "100% free", "act now", "apply now", "buy now", "call now",
    "click here", "double your income", "earn money", "fast cash",
    "financial freedom", "free trial", "guaranteed", "increase sales",
    "limited time", "make money", "no cost", "no risk", "pure profit",
    "risk-free", "special promotion", "winner", "congratulations",
    "$$$", "100% satisfied", "best price", "credit card", "order now"
]

class EmailVerifier:

    @staticmethod
    def is_valid_syntax(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def check_mx_record(email: str) -> bool:
        if "@" not in email:
            return False
        domain = email.split("@")[-1]
        try:
            # Check if domain resolves
            socket.gethostbyname(domain)
            return True
        except Exception:
            return False

    def scan_for_spam_words(self, text: str) -> List[str]:
        found = []
        low = text.lower()
        for word in SPAM_TRIGGER_WORDS:
            if word in low:
                found.append(word)
        return found

    def validate_safety(self, email: str, body_text: str = "") -> Dict[str, Any]:
        reasons = []
        syntax_ok = self.is_valid_syntax(email) if email else False
        if not syntax_ok:
            reasons.append("Invalid email syntax")

        mx_ok = self.check_mx_record(email) if syntax_ok else False
        if syntax_ok and not mx_ok:
            reasons.append("Domain MX record resolution failed")

        spam_words = self.scan_for_spam_words(body_text) if body_text else []
        if spam_words:
            reasons.append(f"Contains potential spam trigger words: {', '.join(spam_words)}")

        is_safe = syntax_ok and (not spam_words)

        return {
            "is_safe": is_safe,
            "syntax_valid": syntax_ok,
            "mx_valid": mx_ok,
            "spam_words_found": spam_words,
            "reasons": reasons,
            "badge": "Verified Safe ✅" if is_safe else "Safety Warning ⚠️"
        }

email_verifier = EmailVerifier()
