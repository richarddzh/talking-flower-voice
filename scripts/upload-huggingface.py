import argparse
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload prepared TalkFlower model and Space packages to Hugging Face."
    )
    parser.add_argument("--model-repo-id", required=True)
    parser.add_argument("--space-repo-id", required=True)
    parser.add_argument(
        "--package",
        default="huggingface_package",
        help="Directory containing model/ and space/ packages",
    )
    parser.add_argument(
        "--private-model",
        action="store_true",
        help="Create the model repo as private instead of the public default",
    )
    parser.add_argument(
        "--private-space",
        action="store_true",
        help="Create the Space as private instead of the public default",
    )
    parser.add_argument("--token-env", default="HF_TOKEN")
    parser.add_argument("--create", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    from huggingface_hub import HfApi

    package_dir = Path(args.package)
    if not package_dir.is_absolute():
        package_dir = REPO_ROOT / package_dir
    model_dir = package_dir / "model"
    space_dir = package_dir / "space"
    if not model_dir.is_dir() or not space_dir.is_dir():
        raise FileNotFoundError(
            f"Expected model and space packages under {package_dir}. "
            "Run scripts/package-huggingface.py first."
        )

    token = os.environ.get(args.token_env)
    api = HfApi(token=token)
    try:
        account = api.whoami()
    except Exception as exc:
        raise RuntimeError(
            "Hugging Face authentication not found. Run `hf auth login` first, "
            f"or set {args.token_env} in the current shell."
        ) from exc
    print(f"Authenticated as: {account['name']}")
    if args.create:
        api.create_repo(
            repo_id=args.model_repo_id,
            repo_type="model",
            private=args.private_model,
            exist_ok=True,
        )
        api.create_repo(
            repo_id=args.space_repo_id,
            repo_type="space",
            space_sdk="gradio",
            private=args.private_space,
            exist_ok=True,
        )

    api.upload_folder(
        repo_id=args.model_repo_id,
        repo_type="model",
        folder_path=str(model_dir),
        commit_message="Upload TalkFlower GPT-SoVITS model",
        ignore_patterns=["__pycache__/**", "*.pyc"],
    )
    api.upload_folder(
        repo_id=args.space_repo_id,
        repo_type="space",
        folder_path=str(space_dir),
        commit_message="Deploy TalkFlower CPU Gradio Space",
        ignore_patterns=["__pycache__/**", "*.pyc", ".runtime_models/**"],
    )
    print(f"Model: https://huggingface.co/{args.model_repo_id}")
    print(f"Space: https://huggingface.co/spaces/{args.space_repo_id}")


if __name__ == "__main__":
    main()
