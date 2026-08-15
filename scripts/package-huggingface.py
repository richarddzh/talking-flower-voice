import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "huggingface_package"

MODEL_ASSETS = [
    (
        "GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt",
        "weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt",
    ),
    (
        "SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth",
        "weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth",
    ),
    (
        "data/smbw_zh_train/audio/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3",
        "reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3",
    ),
]

SPACE_EXCLUDES = shutil.ignore_patterns(
    "__pycache__",
    "*.pyc",
    "pretrained_models",
    "G2PWModel",
    "prepare_datasets",
    "tests",
    "logs",
    "*.wav",
    "*.mp3",
    "*.ckpt",
    "*.pth",
    "*.bin",
    "*.onnx",
)

FASTTEXT_MODEL_URL = (
    "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
)

UPSTREAM_FILES = [
    (
        "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large/config.json",
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/config.json",
        "upstream/lj1995/GPT-SoVITS/chinese-roberta-wwm-ext-large/config.json",
    ),
    (
        "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large/pytorch_model.bin",
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/pytorch_model.bin",
        "upstream/lj1995/GPT-SoVITS/chinese-roberta-wwm-ext-large/pytorch_model.bin",
    ),
    (
        None,
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-roberta-wwm-ext-large/tokenizer.json",
        "upstream/lj1995/GPT-SoVITS/chinese-roberta-wwm-ext-large/tokenizer.json",
    ),
    (
        "GPT_SoVITS/pretrained_models/chinese-hubert-base/config.json",
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/config.json",
        "upstream/lj1995/GPT-SoVITS/chinese-hubert-base/config.json",
    ),
    (
        "GPT_SoVITS/pretrained_models/chinese-hubert-base/pytorch_model.bin",
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/pytorch_model.bin",
        "upstream/lj1995/GPT-SoVITS/chinese-hubert-base/pytorch_model.bin",
    ),
    (
        None,
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/chinese-hubert-base/preprocessor_config.json",
        "upstream/lj1995/GPT-SoVITS/chinese-hubert-base/preprocessor_config.json",
    ),
    (
        None,
        "https://huggingface.co/lj1995/GPT-SoVITS/resolve/main/sv/pretrained_eres2netv2w24s4ep4.ckpt",
        "upstream/lj1995/GPT-SoVITS/sv/pretrained_eres2netv2w24s4ep4.ckpt",
    ),
    (
        None,
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/MONOPHONIC_CHARS.txt",
        "upstream/IQ-Technology/G2PWModel/MONOPHONIC_CHARS.txt",
    ),
    (
        "GPT_SoVITS/text/G2PWModel/POLYPHONIC_CHARS.txt",
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/POLYPHONIC_CHARS.txt",
        "upstream/IQ-Technology/G2PWModel/POLYPHONIC_CHARS.txt",
    ),
    (
        None,
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/bopomofo_to_pinyin_wo_tune_dict.json",
        "upstream/IQ-Technology/G2PWModel/bopomofo_to_pinyin_wo_tune_dict.json",
    ),
    (
        None,
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/char_bopomofo_dict.json",
        "upstream/IQ-Technology/G2PWModel/char_bopomofo_dict.json",
    ),
    (
        None,
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/config.py",
        "upstream/IQ-Technology/G2PWModel/config.py",
    ),
    (
        "GPT_SoVITS/text/G2PWModel/g2pW.onnx",
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/g2pW.onnx",
        "upstream/IQ-Technology/G2PWModel/g2pW.onnx",
    ),
    (
        None,
        "https://huggingface.co/IQ-Technology/G2PWModel/resolve/main/version",
        "upstream/IQ-Technology/G2PWModel/version",
    ),
    (
        None,
        FASTTEXT_MODEL_URL,
        "upstream/facebook/fasttext/lid.176.bin",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Hugging Face model and CPU Space upload folders."
    )
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Package output directory")
    parser.add_argument(
        "--model-repo-id",
        default="richarddzh/talking-flower-voice",
        help="Model repo id embedded in the Space metadata and app",
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Build model metadata and project weights without downloading upstream backups",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite the output directory")
    return parser.parse_args()


def copy_required(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing required asset: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def download_required(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    temp_path = dst.with_suffix(dst.suffix + ".part")
    for attempt in range(1, 4):
        try:
            urllib.request.urlretrieve(url, temp_path)
            temp_path.replace(dst)
            return
        except OSError:
            temp_path.unlink(missing_ok=True)
            if attempt == 3:
                raise
            time.sleep(attempt * 2)


def write_model_files(model_dir: Path, include_upstream: bool = True) -> None:
    for source, destination in MODEL_ASSETS:
        copy_required(REPO_ROOT / source, model_dir / destination)

    manifest = {
        "name": "talkflower_zh_v2pp_strict",
        "framework": "GPT-SoVITS v2ProPlus",
        "gpt_weight": (
            "weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt"
        ),
        "sovits_weight": (
            "weights/SoVITS_weights_v2ProPlus/"
            "talkflower_zh_v2pp_strict_e10_s2120.pth"
        ),
        "reference_audio": (
            "reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3"
        ),
        "reference_text": "只有被选中的人才能得到璀璨的光芒。",
        "text_language": "zh",
        "prompt_language": "zh",
    }
    (model_dir / "talkflower_model.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (model_dir / ".gitattributes").write_text(
        "*.ckpt filter=lfs diff=lfs merge=lfs -text\n"
        "*.pth filter=lfs diff=lfs merge=lfs -text\n"
        "*.bin filter=lfs diff=lfs merge=lfs -text\n"
        "*.onnx filter=lfs diff=lfs merge=lfs -text\n"
        "*.mp3 filter=lfs diff=lfs merge=lfs -text\n",
        encoding="utf-8",
    )
    (model_dir / "README.md").write_text(
        """---
language:
  - zh
license: other
pipeline_tag: text-to-speech
tags:
  - gpt-sovits
  - voice-cloning
  - chinese
---

# 闲聊花花中文 GPT-SoVITS 模型

本仓库包含 `talkflower_zh_v2pp_strict` 的 GPT 与 SoVITS 微调权重，以及默认参考音频。

## 文件

```text
weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt
weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth
reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3
talkflower_model.json
upstream/lj1995/GPT-SoVITS/chinese-roberta-wwm-ext-large/
upstream/lj1995/GPT-SoVITS/chinese-hubert-base/
upstream/lj1995/GPT-SoVITS/sv/pretrained_eres2netv2w24s4ep4.ckpt
upstream/IQ-Technology/G2PWModel/
upstream/facebook/fasttext/lid.176.bin
```

模型基于 GPT-SoVITS v2ProPlus。为防止上游文件删除或变更，本仓库固定备份了运行所需的通用模型资产，Space 只从本仓库下载这些副本。

## 上游备份来源

| 本仓库路径 | 原始仓库 | 原始路径 |
| --- | --- | --- |
| `upstream/lj1995/GPT-SoVITS/chinese-roberta-wwm-ext-large` | `lj1995/GPT-SoVITS` | `chinese-roberta-wwm-ext-large/` |
| `upstream/lj1995/GPT-SoVITS/chinese-hubert-base` | `lj1995/GPT-SoVITS` | `chinese-hubert-base/` |
| `upstream/lj1995/GPT-SoVITS/sv/pretrained_eres2netv2w24s4ep4.ckpt` | `lj1995/GPT-SoVITS` | `sv/pretrained_eres2netv2w24s4ep4.ckpt` |
| `upstream/IQ-Technology/G2PWModel` | `IQ-Technology/G2PWModel` | 仓库根目录 |
| `upstream/facebook/fasttext/lid.176.bin` | Facebook FastText | `https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin` |

这些文件是第三方通用依赖，不是闲聊花花微调产物；保留原始路径和来源仅用于可复现备份。使用时还需遵守各上游项目的许可证和模型条款。

## 权限与用途

本模型模仿游戏角色风格，仅供研究和技术演示。上传或公开分享前，请确认你拥有原始语音、参考音频及衍生权重的分发权限。不得用于欺骗、冒充或其他侵权用途。
""",
        encoding="utf-8",
    )

    if include_upstream:
        for local_source, url, destination in UPSTREAM_FILES:
            destination_path = model_dir / destination
            source_path = REPO_ROOT / local_source if local_source else None
            if source_path and source_path.exists():
                copy_required(source_path, destination_path)
            else:
                download_required(url, destination_path)


def write_space_files(space_dir: Path, model_repo_id: str) -> None:
    shutil.copytree(
        REPO_ROOT / "GPT_SoVITS",
        space_dir / "GPT_SoVITS",
        ignore=SPACE_EXCLUDES,
    )
    shutil.copytree(
        REPO_ROOT / "tools",
        space_dir / "tools",
        ignore=SPACE_EXCLUDES,
    )
    for filename in ["app.py", "requirements.txt", "README.md"]:
        copy_required(
            REPO_ROOT / "huggingface_space" / filename,
            space_dir / filename,
        )
    copy_required(REPO_ROOT / "LICENSE", space_dir / "LICENSE")
    copy_required(
        REPO_ROOT / "docs" / "THIRD_PARTY_SOURCES.md",
        space_dir / "THIRD_PARTY_SOURCES.md",
    )

    app_path = space_dir / "app.py"
    app_path.write_text(
        app_path.read_text(encoding="utf-8").replace(
            '"richarddzh/talking-flower-voice"', f'"{model_repo_id}"', 1
        ),
        encoding="utf-8",
    )
    readme_path = space_dir / "README.md"
    readme_path.write_text(
        readme_path.read_text(encoding="utf-8").replace(
            "  - richarddzh/talking-flower-voice",
            f"  - {model_repo_id}",
            1,
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output).resolve()
    if output_dir.exists():
        if not args.force:
            raise FileExistsError(
                f"Package directory already exists: {output_dir}. Use --force to overwrite."
            )
        shutil.rmtree(output_dir)

    model_dir = output_dir / "model"
    space_dir = output_dir / "space"
    model_dir.mkdir(parents=True)
    space_dir.mkdir(parents=True)
    write_model_files(model_dir, include_upstream=not args.metadata_only)
    write_space_files(space_dir, args.model_repo_id)

    for label, path in [("Model", model_dir), ("Space", space_dir)]:
        files = [item for item in path.rglob("*") if item.is_file()]
        size = sum(item.stat().st_size for item in files)
        print(f"{label} package: {path}")
        print(f"{label} files: {len(files)}")
        print(f"{label} size MB: {size / 1024 / 1024:.2f}")


if __name__ == "__main__":
    main()
