import argparse
import json
import re
from pathlib import Path


CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Filter GPT-SoVITS list files for fragmented Chinese speech.")
    parser.add_argument("--input", required=True, help="Input list file: wav|speaker|lang|text")
    parser.add_argument("--output", required=True, help="Filtered output list path")
    parser.add_argument("--dropped", required=True, help="JSON report for dropped rows")
    parser.add_argument("--min-cjk", type=int, default=4, help="Minimum number of CJK characters to keep")
    parser.add_argument(
        "--exclude-name-regex",
        action="append",
        default=[],
        help="Regex applied to audio file name. Can be specified multiple times.",
    )
    return parser.parse_args()


def cjk_count(text: str) -> int:
    return len(CJK_RE.findall(text))


def read_list(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8-sig")
    return [line.strip() for line in content.splitlines() if line.strip()]


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    dropped_path = Path(args.dropped)
    exclude_patterns = [re.compile(pattern) for pattern in args.exclude_name_regex]

    kept: list[str] = []
    dropped: list[dict[str, object]] = []

    for line in read_list(input_path):
        parts = line.split("|", 3)
        if len(parts) != 4:
            dropped.append({"reason": "invalid_line", "line": line})
            continue

        audio_path, speaker, language, text = parts
        name = Path(audio_path).name
        count = cjk_count(text)
        reason = ""

        if count < args.min_cjk:
            reason = f"text_cjk_len_lt_{args.min_cjk}"
        else:
            for pattern in exclude_patterns:
                if pattern.search(name):
                    reason = f"exclude_name_regex:{pattern.pattern}"
                    break

        if reason:
            dropped.append(
                {
                    "reason": reason,
                    "name": name,
                    "text": text,
                    "cjk_count": count,
                    "path": audio_path,
                    "speaker": speaker,
                    "language": language,
                }
            )
        else:
            kept.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    dropped_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    dropped_path.write_text(json.dumps(dropped, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Input rows: {len(kept) + len(dropped)}")
    print(f"Kept rows: {len(kept)}")
    print(f"Dropped rows: {len(dropped)}")
    print(f"Filtered list: {output_path}")
    print(f"Dropped report: {dropped_path}")


if __name__ == "__main__":
    main()
