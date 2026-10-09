import json
from dataclasses import asdict, dataclass
from pathlib import Path

# inventory.py is inside app/practice.
APP_DIR = Path(__file__).resolve().parent.parent
print(f"APP_DIR: {APP_DIR}")
INPUT_DIR = APP_DIR / "data"
OUTPUT_PATH = APP_DIR / "practice" / "output" / "document_inventory.json"


@dataclass(frozen=True)
class SchoolDocument:
    filename: str
    title: str
    language: str
    word_count: int
    character_count: int


def language_from_filename(path: Path) -> str:
    """Extract language from filenames such as fees_en.txt."""
    language = path.stem.rsplit("_", maxsplit=1)[-1].lower()

    if language in {"en", "hi", "or"}:
        return language

    return "unknown"


def read_document(path: Path) -> SchoolDocument:
    """Read a UTF-8 text file and create its metadata."""
    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError("Document is empty")

    return SchoolDocument(
        filename=path.name,
        title=text.splitlines()[0].strip(),
        language=language_from_filename(path),
        word_count=len(text.split()),
        character_count=len(text),
    )


def build_inventory(
    folder: Path,
) -> tuple[list[SchoolDocument], list[str]]:
    """Process text files, recording failures separately."""
    if not folder.is_dir():
        raise FileNotFoundError(f"Input folder not found: {folder}")

    documents: list[SchoolDocument] = []
    failures: list[str] = []

    for path in sorted(folder.glob("*.txt")):
        if not path.is_file():
            continue

        try:
            document = read_document(path)
            documents.append(document)
        except (OSError, UnicodeError, ValueError) as error:
            failures.append(f"{path.name}: {error}")

    return documents, failures


def save_inventory(
    documents: list[SchoolDocument],
    failures: list[str],
    output_path: Path,
) -> None:
    """Convert document objects to dictionaries and save JSON."""
    report = {
        "document_count": len(documents),
        "failure_count": len(failures),
        "documents": [asdict(document) for document in documents],
        "failures": failures,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    print(f"Reading files from: {INPUT_DIR}\n")

    try:
        documents, failures = build_inventory(INPUT_DIR)
        save_inventory(documents, failures, OUTPUT_PATH)
    except OSError as error:
        print(f"Inventory could not be created: {error}")
        raise SystemExit(1) from error

    print(f"{'Filename':<25} {'Language':<10} {'Words':>8}")
    print("-" * 45)

    for document in documents:
        print(f"{document.filename:<25} " f"{document.language:<10} " f"{document.word_count:>8}")

    for failure in failures:
        print(f"\nFAILED: {failure}")

    if not documents and not failures:
        print("\nNo .txt files found in the input folder.")

    print(f"\nSuccessful documents: {len(documents)}")
    print(f"Failed documents: {len(failures)}")
    print(f"JSON saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
