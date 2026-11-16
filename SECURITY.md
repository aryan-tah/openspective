# Security policy

## Supported versions

Security fixes go into the latest release.

## Reporting a vulnerability

Please don't open a public issue for security problems. Report them privately through GitHub: **Security → Report a vulnerability** on this repository. You'll get an acknowledgement within three days.

openspective is a network service that receives user-generated text and, optionally, API keys. Things worth reporting include ways to bypass API key checks, read other clients' data (for example stored feedback), make the server load arbitrary models or files, or exhaust it with a single request.

openspective never stores comment text unless you turn on feedback storage for `comments:suggestscore`.
