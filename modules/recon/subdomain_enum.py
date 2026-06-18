#!/usr/bin/env python3
"""
Subdomain enumeration module — multi-tool approach.
Works on Linux, Windows, Termux.
"""

import subprocess
import json
import dns.resolver
import logging
from typing import List, Dict, Any

class SubdomainEnumerator:
    """
    Enumerate subdomains using multiple techniques:
    - DNS brute-force
    - Certificate transparency logs
    - Search engine scraping (passive)
    """
    
    def __init__(self, domain: str, wordlist: str = None):
        self.domain = domain
        self.wordlist = wordlist or self._default_wordlist()
        self.logger = logging.getLogger("SubdomainEnum")
        self.results = set()
        
    def _default_wordlist(self) -> List[str]:
        """Common subdomain wordlist (built-in, no external dependency)."""
        return [
            "www", "mail", "ftp", "admin", "api", "dev", "test", "staging",
            "blog", "shop", "portal", "vpn", "remote", "secure", "webmail",
            "support", "help", "cdn", "static", "assets", "images", "img",
            "video", "docs", "wiki", "forum", "chat", "app", "mobile",
            "m", "ns1", "ns2", "mx", "smtp", "pop3", "imap", "cloud",
            "jenkins", "gitlab", "jira", "confluence", "grafana", "prometheus",
            "kibana", "elastic", "monitor", "status", "dashboard", "metrics"
        ]
    
    def dns_bruteforce(self) -> List[str]:
        """Brute-force subdomains via DNS queries."""
        found = []
        resolver = dns.resolver.Resolver()
        resolver.timeout = 2
        resolver.lifetime = 2
        
        for sub in self._get_wordlist():
            try:
                fqdn = f"{sub}.{self.domain}"
                answers = resolver.resolve(fqdn, "A")
                if answers:
                    ips = [str(r) for r in answers]
                    found.append({"subdomain": fqdn, "ips": ips, "type": "dns_bruteforce"})
                    self.logger.info(f"Found: {fqdn} -> {ips}")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, 
                    dns.resolver.Timeout, dns.exception.DNSException):
                pass
        
        self.results.update([f["subdomain"] for f in found])
        return found
    
    def crtsh_enum(self) -> List[str]:
        """Query Certificate Transparency logs (crt.sh)."""
        import requests
        found = []
        try:
            url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                for entry in data:
                    name = entry.get("name_value", "")
                    if name and self.domain in name:
                        for sub in name.split("\n"):
                            sub = sub.strip()
                            if sub and sub not in self.results:
                                found.append({"subdomain": sub, "type": "certificate_transparency"})
                                self.results.add(sub)
        except Exception as e:
            self.logger.warning(f"crt.sh query failed: {e}")
        
        return found
    
    def _get_wordlist(self) -> List[str]:
        """Get the wordlist (file or built-in)."""
        if isinstance(self.wordlist, str) and os.path.exists(self.wordlist):
            with open(self.wordlist) as f:
                return [line.strip() for line in f if line.strip()]
        return self.wordlist
    
    def enumerate_all(self) -> Dict[str, Any]:
        """Run all enumeration techniques."""
        results = {
            "domain": self.domain,
            "dns_bruteforce": self.dns_bruteforce(),
            "crtsh": self.crtsh_enum(),
            "unique_subdomains": sorted(self.results),
            "count": len(self.results)
        }
        return results