from typing import List

import aiohttp


class DNSLookupError(Exception):
    """The lookup itself failed (network/server error) — distinct from 'no such record'."""


class DoHResolver:
    """DNS-over-HTTPS (Cloudflare JSON API). Free, keyless, no extra dependency."""

    URL = "https://cloudflare-dns.com/dns-query"

    async def query(self, name: str, rtype: str) -> List[str]:
        """Returns record values ([] for NXDOMAIN / no records). TXT strings are
        unquoted and their chunks joined. Raises DNSLookupError on lookup failure."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
                async with session.get(
                    self.URL, params={"name": name, "type": rtype},
                    headers={"accept": "application/dns-json"},
                ) as resp:
                    if resp.status != 200:
                        raise DNSLookupError(f"DoH HTTP {resp.status} for {rtype} {name}")
                    data = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise DNSLookupError(str(err)) from err

        status = data.get("Status")
        if status == 3:  # NXDOMAIN
            return []
        if status != 0:
            raise DNSLookupError(f"DoH status {status} for {rtype} {name}")

        values = []
        for ans in data.get("Answer", []) or []:
            raw = ans.get("data", "")
            if rtype.upper() == "TXT":
                raw = "".join(part for part in raw.replace('" "', "\x00").strip('"').split("\x00"))
            values.append(raw)
        return values
