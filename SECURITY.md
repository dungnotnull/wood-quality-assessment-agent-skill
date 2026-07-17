# Security Policy

## Supported Versions

wood-quality-assessment is a development-skill project. Security fixes are
applied to the latest released version only.

| Version | Supported          |
|---------|--------------------|
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability — for example a payload in
`SECOND-KNOWLEDGE-BRAIN.md` crawl data that could cause unsafe behavior, or a
defect in `tools/knowledge_updater.py` that mishandles untrusted remote
responses — please report it responsibly:

1. **Do not open a public issue.**
2. Open a private security advisory via the repository's "Security" tab, or
   email the maintainer directly if the repository lists a contact.
3. Include: a description of the issue, steps to reproduce, and the impact
   you foresee.

You will receive an acknowledgment within 72 hours. We will coordinate a fix
and disclosure timeline with you.

## Security Considerations for This Project

- `tools/knowledge_updater.py` fetches from public academic/news APIs
  (Semantic Scholar, ArXiv, CITES/ITTO RSS). Remote responses are parsed
  defensively and never `eval`'d or `exec`'d; XML/JSON parse failures degrade
  gracefully to empty results.
- The pipeline appends markdown to `SECOND-KNOWLEDGE-BRAIN.md`. Crawl data is
  treated as untrusted text: it is rendered as markdown only and never
  executed as code.
- No secrets, API keys, or credentials are required or stored by the project.
- Network timeouts are enforced (default 30s) to prevent hanging on
  unreachable sources.

## Best-Practice Deployment

- Run the weekly crawl under a non-privileged service account.
- Pin dependency versions in production (`pip install -r requirements.txt`).
- Review appended `SECOND-KNOWLEDGE-BRAIN.md` entries periodically; the crawl
  pipeline surfaces but does not verify the scientific accuracy of remote
  sources.
