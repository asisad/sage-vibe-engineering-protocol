"""Allow ``python -m sage_sdk`` to use the SDK CLI."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
