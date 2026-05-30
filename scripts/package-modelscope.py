import argparse
import json
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

ASSETS = [
    ("GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt", "weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt"),
    ("SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth", "weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth"),
    ("data/smbw_zh_train/audio/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3", "reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3"),
    ("requirements-inference.txt", "requirements-inference.txt"),
    ("scripts/talkflower-tts.py", "scripts/talkflower-tts.py"),
    ("scripts/infer-talkflower.ps1", "scripts/infer-talkflower.ps1"),
    ("scripts/benchmark-talkflower.ps1", "scripts/benchmark-talkflower.ps1"),
    ("docs/USAGE.md", "docs/USAGE.md"),
    ("docs/DEPENDENCIES.md", "docs/DEPENDENCIES.md"),
    ("docs/PRINCIPLES.md", "docs/PRINCIPLES.md"),
    ("docs/THIRD_PARTY_SOURCES.md", "docs/THIRD_PARTY_SOURCES.md"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a ModelScope-ready local package for TalkFlower inference.")
    parser.add_argument("--output", default="modelscope_package/talkflower_zh_v2pp_strict", help="Package output directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing package directory")
    return parser.parse_args()


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Missing required asset: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_model_card(output_dir: Path) -> None:
    readme = """# 闲聊花花中文 GPT-SoVITS 语音模型

本模型是基于 GPT-SoVITS v2ProPlus 微调得到的中文 TTS 语音模型，用于生成“闲聊花花”角色风格语音。

## 文件结构

```text
weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt
weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth
reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3
requirements-inference.txt
scripts/talkflower-tts.py
scripts/infer-talkflower.ps1
scripts/benchmark-talkflower.ps1
docs/
```

## 运行依赖

本包只包含本项目微调权重、参考音频和推理脚本。运行前仍需准备 GPT-SoVITS 推理代码和以下开源预训练资产：

- `GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large`
- `GPT_SoVITS/pretrained_models/chinese-hubert-base`
- `GPT_SoVITS/text/G2PWModel`

详见 `docs/DEPENDENCIES.md`。

## 默认推理配置

| 项目 | 值 |
| --- | --- |
| GPT 权重 | `weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt` |
| SoVITS 权重 | `weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth` |
| 参考音频 | `reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3` |
| 参考文本 | `只有被选中的人才能得到璀璨的光芒。` |

## 权限说明

请仅在你拥有相关语音素材和衍生模型分发权限的前提下上传或公开分享本模型包。
"""
    (output_dir / "README.md").write_text(readme, encoding="utf-8")


def write_manifest(output_dir: Path) -> None:
    manifest = {
        "name": "talkflower_zh_v2pp_strict",
        "framework": "GPT-SoVITS v2ProPlus",
        "gpt_weight": "weights/GPT_weights_v2ProPlus/talkflower_zh_v2pp_strict-e18.ckpt",
        "sovits_weight": "weights/SoVITS_weights_v2ProPlus/talkflower_zh_v2pp_strict_e10_s2120.pth",
        "reference_audio": "reference/TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3",
        "reference_text": "只有被选中的人才能得到璀璨的光芒。",
        "text_language": "zh",
        "prompt_language": "zh",
    }
    (output_dir / "talkflower_model.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    if output_dir.exists():
        if not args.force:
            raise FileExistsError(f"Package directory already exists: {output_dir}. Use --force to overwrite.")
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True)
    for src, dst in ASSETS:
        copy_file(REPO_ROOT / src, output_dir / dst)
    write_model_card(output_dir)
    write_manifest(output_dir)

    total_size = sum(path.stat().st_size for path in output_dir.rglob("*") if path.is_file())
    print(f"ModelScope package: {output_dir}")
    print(f"Files: {sum(1 for path in output_dir.rglob('*') if path.is_file())}")
    print(f"Size MB: {total_size / 1024 / 1024:.2f}")


if __name__ == "__main__":
    main()
