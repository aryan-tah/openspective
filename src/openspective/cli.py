"""Command line: `openspective serve`, `openspective score`, `openspective download`."""

from __future__ import annotations

import argparse
import json
import os
import sys

from openspective import __version__


def _serve(args: argparse.Namespace) -> int:
    import uvicorn

    if args.backend:
        os.environ["OPENSPECTIVE_BACKEND"] = args.backend
    uvicorn.run(
        "openspective.app:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level=args.log_level,
    )
    return 0


def _score(args: argparse.Namespace) -> int:
    from openspective.backends import load
    from openspective.language import LanguageDetector
    from openspective.schema import AnalyzeCommentRequest
    from openspective.service import Analyzer

    text = sys.stdin.read() if args.text == "-" else args.text
    analyzer = Analyzer(load(args.backend or "detoxify"), LanguageDetector())
    request = AnalyzeCommentRequest.model_validate(
        {
            "comment": {"text": text},
            "requestedAttributes": {a: {} for a in args.attributes},
            "languages": [args.language] if args.language else None,
            "spanAnnotations": args.spans,
            "dropUnsupportedAttributes": True,
        }
    )
    print(json.dumps(analyzer.analyze(request).to_json(), indent=2, ensure_ascii=False))
    return 0


def _download(_: argparse.Namespace) -> int:
    from openspective.backends.detoxify import DetoxifyBackend

    DetoxifyBackend().preload()
    print("Models downloaded.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="openspective", description=__doc__)
    parser.add_argument("--version", action="version", version=f"openspective {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Run the Perspective-compatible HTTP server.")
    serve.add_argument("--host", default=os.environ.get("OPENSPECTIVE_HOST", "127.0.0.1"))
    serve.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    serve.add_argument("--workers", type=int, default=1)
    serve.add_argument("--backend", choices=["detoxify", "fake"])
    serve.add_argument("--log-level", default="info")
    serve.set_defaults(func=_serve)

    score = sub.add_parser("score", help="Score one comment and print the API response.")
    score.add_argument("text", help="Comment text, or - to read stdin.")
    score.add_argument(
        "-a",
        "--attributes",
        nargs="+",
        default=["TOXICITY", "SEVERE_TOXICITY", "IDENTITY_ATTACK", "INSULT", "PROFANITY", "THREAT"],
    )
    score.add_argument("-l", "--language")
    score.add_argument("--spans", action="store_true", help="Score each sentence too.")
    score.add_argument("--backend", choices=["detoxify", "fake"])
    score.set_defaults(func=_score)

    download = sub.add_parser("download", help="Download the models ahead of time (for images and CI).")
    download.set_defaults(func=_download)

    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
