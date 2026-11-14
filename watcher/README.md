# watcher

Optional Tier 2: a small multi-arch Docker image that opens the launcher tile
on TV power-on and after Home. Needs one firewall rule (watcher host -> TV,
TCP 36669 only). The Hisense client certificate is never shipped; each user
extracts their own. See [../docs/03-architecture.md](../docs/03-architecture.md).

**Status:** planned
