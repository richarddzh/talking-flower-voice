import argparse
import json
import os
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from GPT_SoVITS.TTS_infer_pack.TTS import TTS  # noqa: E402


DEFAULT_TEXT = "你好，我是闲聊花花。今天也一起开心地冒险吧。"
DEFAULT_REF_TEXT = "只有被选中的人才能得到璀璨的光芒。"
DEFAULT_REF_AUDIO = REPO_ROOT / "data" / "smbw_zh_train" / "audio" / "TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3"
DEFAULT_GPT = REPO_ROOT / "GPT_weights_v2ProPlus" / "talkflower_zh_v2pp_strict-e18.ckpt"
DEFAULT_SOVITS = REPO_ROOT / "SoVITS_weights_v2ProPlus" / "talkflower_zh_v2pp_strict_e10_s2120.pth"
DEFAULT_BERT = REPO_ROOT / "GPT_SoVITS" / "pretrained_models" / "chinese-roberta-wwm-ext-large"
DEFAULT_HUBERT = REPO_ROOT / "GPT_SoVITS" / "pretrained_models" / "chinese-hubert-base"


def existing_path(value: str | Path, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"{label} not found: {path}")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TalkFlower voice pack inference and benchmark helper.")
    parser.add_argument("--text", default=DEFAULT_TEXT, help="Text to synthesize")
    parser.add_argument("--output", default=str(REPO_ROOT / "outputs" / "talkflower_latest.wav"), help="Output wav path")
    parser.add_argument("--device", choices=["cuda", "cpu"], default="cuda", help="Inference device")
    parser.add_argument("--is-half", action="store_true", help="Use fp16 on CUDA")
    parser.add_argument("--gpt", default=str(DEFAULT_GPT), help="GPT weight path")
    parser.add_argument("--sovits", default=str(DEFAULT_SOVITS), help="SoVITS weight path")
    parser.add_argument("--ref-audio", default=str(DEFAULT_REF_AUDIO), help="Reference audio path")
    parser.add_argument("--ref-text", default=DEFAULT_REF_TEXT, help="Reference text")
    parser.add_argument("--text-lang", default="zh", help="Target language code")
    parser.add_argument("--prompt-lang", default="zh", help="Prompt language code")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--repetition-penalty", type=float, default=1.35)
    parser.add_argument("--text-split-method", default="cut5")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--benchmark", action="store_true", help="Run timing benchmark")
    parser.add_argument("--warmup", type=int, default=1, help="Benchmark warmup runs")
    parser.add_argument("--runs", type=int, default=3, help="Benchmark measured runs")
    parser.add_argument("--report", default="", help="Optional benchmark JSON report path")
    return parser.parse_args()


def build_tts(args: argparse.Namespace) -> TTS:
    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. Use --device cpu for CPU inference.")

    config = {
        "custom": {
            "device": args.device,
            "is_half": bool(args.is_half and args.device == "cuda"),
            "version": "v2ProPlus",
            "t2s_weights_path": str(existing_path(args.gpt, "GPT weight")),
            "vits_weights_path": str(existing_path(args.sovits, "SoVITS weight")),
            "bert_base_path": str(existing_path(DEFAULT_BERT, "BERT model")),
            "cnhuhbert_base_path": str(existing_path(DEFAULT_HUBERT, "CNHuBERT model")),
        }
    }

    tmp_dir = REPO_ROOT / "TEMP"
    tmp_dir.mkdir(exist_ok=True)
    config_path = tmp_dir / f"tts_infer_{args.device}.yaml"
    config_path.write_text(yaml.dump(config, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    tts = TTS(str(config_path))
    config_path.unlink(missing_ok=True)
    return tts


def synthesize(tts: TTS, args: argparse.Namespace) -> tuple[float, int, object]:
    inputs = {
        "text": args.text,
        "text_lang": args.text_lang,
        "ref_audio_path": str(existing_path(args.ref_audio, "Reference audio")),
        "prompt_text": args.ref_text,
        "prompt_lang": args.prompt_lang,
        "top_k": args.top_k,
        "top_p": args.top_p,
        "temperature": args.temperature,
        "text_split_method": args.text_split_method,
        "batch_size": args.batch_size,
        "batch_threshold": 0.75,
        "split_bucket": True,
        "speed_factor": 1.0,
        "fragment_interval": 0.3,
        "seed": args.seed,
        "parallel_infer": True,
        "repetition_penalty": args.repetition_penalty,
        "return_fragment": False,
        "streaming_mode": False,
    }

    if args.device == "cuda":
        torch.cuda.synchronize()
    start = time.perf_counter()
    outputs = list(tts.run(inputs))
    if not outputs:
        raise RuntimeError("TTS inference returned no audio.")
    sr, audio = outputs[-1]
    if args.device == "cuda":
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - start
    return elapsed, int(sr), audio


def run_once(tts: TTS, args: argparse.Namespace) -> tuple[float, int, int]:
    elapsed, sr, audio = synthesize(tts, args)
    return elapsed, sr, len(audio)


def benchmark(tts: TTS, args: argparse.Namespace) -> dict[str, object]:
    for _ in range(max(0, args.warmup)):
        run_once(tts, args)

    rows = []
    for index in range(args.runs):
        elapsed, sr, audio_len = run_once(tts, args)
        audio_seconds = audio_len / sr
        rows.append(
            {
                "run": index + 1,
                "elapsed_seconds": elapsed,
                "audio_seconds": audio_seconds,
                "rtf": elapsed / audio_seconds if audio_seconds else None,
            }
        )
        print(
            f"run={index + 1} device={args.device} elapsed={elapsed:.3f}s "
            f"audio={audio_seconds:.3f}s rtf={rows[-1]['rtf']:.4f}"
        )

    avg_elapsed = sum(row["elapsed_seconds"] for row in rows) / len(rows)
    avg_audio = sum(row["audio_seconds"] for row in rows) / len(rows)
    report = {
        "device": args.device,
        "is_half": bool(args.is_half and args.device == "cuda"),
        "text": args.text,
        "runs": rows,
        "average_elapsed_seconds": avg_elapsed,
        "average_audio_seconds": avg_audio,
        "average_rtf": avg_elapsed / avg_audio if avg_audio else None,
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "",
    }

    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = REPO_ROOT / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
        print(f"Report: {report_path}")

    return report


def main() -> None:
    os.chdir(REPO_ROOT)
    args = parse_args()
    Path(REPO_ROOT / "outputs").mkdir(exist_ok=True)
    tts = build_tts(args)

    if args.benchmark:
        benchmark(tts, args)
    else:
        elapsed, sr, audio = synthesize(tts, args)
        print(f"Elapsed seconds: {elapsed:.3f}")
        print(f"Audio seconds: {len(audio) / sr:.3f}")
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        sf.write(output_path, audio, sr)
        print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
