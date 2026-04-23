import sys
import argparse
from pathlib import Path

from app.config.db import SessionLocal
from app.services.document_process_service import process_document_embedding


def main():
    parser = argparse.ArgumentParser(description="Run document embedding pipeline directly")
    parser.add_argument("input_dir", help="Path to directory containing documents to process")
    args = parser.parse_args()

    Path("app/static").mkdir(parents=True, exist_ok=True)

    session = SessionLocal()
    try:
        count = process_document_embedding(session, args.input_dir)
        print(f"Processed {count} documents from {args.input_dir}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()