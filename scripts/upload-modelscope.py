import argparse
import os
from pathlib import Path

from modelscope.hub.api import HubApi


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload a prepared TalkFlower package to ModelScope.")
    parser.add_argument("--repo-id", required=True, help="ModelScope repo id, for example namespace/model-name")
    parser.add_argument("--package", default="modelscope_package/talkflower_zh_v2pp_strict", help="Prepared package directory")
    parser.add_argument("--private", action="store_true", help="Create/upload as a private model repo")
    parser.add_argument("--token-env", default="MODELSCOPE_TOKEN", help="Environment variable containing ModelScope token")
    parser.add_argument("--create", action="store_true", help="Create repo if it does not exist")
    parser.add_argument("--commit-message", default="Upload TalkFlower GPT-SoVITS inference package")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package_dir = Path(args.package)
    if not package_dir.is_absolute():
        package_dir = REPO_ROOT / package_dir
    if not package_dir.exists():
        raise FileNotFoundError(f"Package directory not found: {package_dir}. Run scripts/package-modelscope.py first.")

    token = os.environ.get(args.token_env)
    api = HubApi()
    if token:
        api.login(access_token=token)

    if args.create:
        visibility = "private" if args.private else "public"
        api.create_repo(
            repo_id=args.repo_id,
            repo_type="model",
            visibility=visibility,
            license="other",
            exist_ok=True,
            token=token,
        )

    api.upload_folder(
        repo_id=args.repo_id,
        folder_path=str(package_dir),
        repo_type="model",
        commit_message=args.commit_message,
        token=token,
        ignore_patterns=[".git/**", "__pycache__/**"],
    )
    print(f"Uploaded package to ModelScope: {args.repo_id}")


if __name__ == "__main__":
    main()
