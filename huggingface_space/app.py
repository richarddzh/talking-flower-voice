import os
import sys
import threading
from pathlib import Path

import gradio as gr
import librosa
import numpy as np
import torch
from huggingface_hub import snapshot_download


SPACE_ROOT = Path(__file__).resolve().parent
GPT_SOVITS_ROOT = SPACE_ROOT / "GPT_SoVITS"
MODEL_REPO_ID = os.environ.get("TALKFLOWER_MODEL_REPO", "richarddzh/talking-flower-voice")

DEFAULT_TEXT = "你好，我是闲聊花花。今天也一起开心地冒险吧。"
DEFAULT_REF_TEXT = "只有被选中的人才能得到璀璨的光芒。"
MAX_TEXT_LENGTH = 120

_load_lock = threading.Lock()
_inference_lock = threading.Lock()
_tts = None
_model_dir = None


def _require_files(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing runtime assets:\n" + "\n".join(missing))


def _prepare_runtime() -> Path:
    global _model_dir
    if _model_dir is not None:
        return _model_dir

    model_dir = Path(
        snapshot_download(
            repo_id=MODEL_REPO_ID,
            repo_type="model",
            allow_patterns=[
                "weights/**",
                "reference/**",
                "upstream/**",
                "talkflower_model.json",
            ],
            token=os.environ.get("HF_TOKEN"),
        )
    )

    upstream_root = model_dir / "upstream"
    pretrained_dir = GPT_SOVITS_ROOT / "pretrained_models"
    roberta_dir = (
        upstream_root / "lj1995" / "GPT-SoVITS" / "chinese-roberta-wwm-ext-large"
    )
    hubert_dir = upstream_root / "lj1995" / "GPT-SoVITS" / "chinese-hubert-base"
    sv_checkpoint = (
        upstream_root
        / "lj1995"
        / "GPT-SoVITS"
        / "sv"
        / "pretrained_eres2netv2w24s4ep4.ckpt"
    )
    fasttext_model = (
        upstream_root / "facebook" / "fasttext" / "lid.176.bin"
    )
    g2pw_dir = upstream_root / "IQ-Technology" / "G2PWModel"

    _require_files(
        [
            model_dir / "weights" / "GPT_weights_v2ProPlus" / "talkflower_zh_v2pp_strict-e18.ckpt",
            model_dir
            / "weights"
            / "SoVITS_weights_v2ProPlus"
            / "talkflower_zh_v2pp_strict_e10_s2120.pth",
            model_dir / "reference" / "TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3",
            roberta_dir / "pytorch_model.bin",
            roberta_dir / "tokenizer.json",
            hubert_dir / "pytorch_model.bin",
            hubert_dir / "preprocessor_config.json",
            sv_checkpoint,
            fasttext_model,
            g2pw_dir / "g2pW.onnx",
            g2pw_dir / "config.py",
            g2pw_dir / "MONOPHONIC_CHARS.txt",
        ]
    )

    pretrained_dir.mkdir(parents=True, exist_ok=True)
    (pretrained_dir / "chinese-roberta-wwm-ext-large").symlink_to(
        roberta_dir, target_is_directory=True
    )
    (pretrained_dir / "chinese-hubert-base").symlink_to(
        hubert_dir, target_is_directory=True
    )
    (pretrained_dir / "sv").mkdir(exist_ok=True)
    (pretrained_dir / "sv" / sv_checkpoint.name).symlink_to(sv_checkpoint)
    fast_langdetect_dir = pretrained_dir / "fast_langdetect"
    fast_langdetect_dir.mkdir(exist_ok=True)
    (fast_langdetect_dir / fasttext_model.name).symlink_to(fasttext_model)
    g2pw_target = GPT_SOVITS_ROOT / "text" / "G2PWModel"
    g2pw_target.symlink_to(g2pw_dir, target_is_directory=True)

    os.environ["bert_path"] = str(roberta_dir)
    _model_dir = model_dir
    return model_dir


def _load_tts():
    global _tts
    if _tts is not None:
        return _tts

    with _load_lock:
        if _tts is not None:
            return _tts

        model_dir = _prepare_runtime()
        sys.path.insert(0, str(SPACE_ROOT))
        sys.path.insert(0, str(GPT_SOVITS_ROOT))

        from TTS_infer_pack.TTS import TTS

        _tts = TTS(
            {
                "custom": {
                    "device": "cpu",
                    "is_half": False,
                    "version": "v2ProPlus",
                    "t2s_weights_path": str(
                        model_dir
                        / "weights"
                        / "GPT_weights_v2ProPlus"
                        / "talkflower_zh_v2pp_strict-e18.ckpt"
                    ),
                    "vits_weights_path": str(
                        model_dir
                        / "weights"
                        / "SoVITS_weights_v2ProPlus"
                        / "talkflower_zh_v2pp_strict_e10_s2120.pth"
                    ),
                    "bert_base_path": str(
                        model_dir
                        / "upstream"
                        / "lj1995"
                        / "GPT-SoVITS"
                        / "chinese-roberta-wwm-ext-large"
                    ),
                    "cnhuhbert_base_path": str(
                        model_dir
                        / "upstream"
                        / "lj1995"
                        / "GPT-SoVITS"
                        / "chinese-hubert-base"
                    ),
                }
            }
        )
        return _tts


def _shift_pitch(audio: np.ndarray, sample_rate: int, semitones: float) -> np.ndarray:
    if abs(semitones) < 0.01:
        return audio

    audio_float = audio.astype(np.float32)
    if np.issubdtype(audio.dtype, np.integer):
        audio_float /= np.iinfo(audio.dtype).max
    speed_ratio = 2 ** (semitones / 12)
    shifted = librosa.resample(
        audio_float,
        orig_sr=sample_rate,
        target_sr=sample_rate / speed_ratio,
        res_type="soxr_hq",
    )
    return np.clip(shifted, -1.0, 1.0)


def synthesize(
    text: str,
    pitch_semitones: float,
    temperature: float,
    repetition_penalty: float,
):
    text = text.strip()
    if not text:
        raise gr.Error("请输入要生成的文字。")
    if len(text) > MAX_TEXT_LENGTH:
        raise gr.Error(f"CPU Basic 单次最多输入 {MAX_TEXT_LENGTH} 个字符。")

    model_dir = _prepare_runtime()
    inputs = {
        "text": text,
        "text_lang": "zh",
        "ref_audio_path": str(
            model_dir / "reference" / "TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3"
        ),
        "prompt_text": DEFAULT_REF_TEXT,
        "prompt_lang": "zh",
        "top_k": 5,
        "top_p": 1.0,
        "temperature": temperature,
        "text_split_method": "cut5",
        "batch_size": 1,
        "batch_threshold": 0.75,
        "split_bucket": True,
        "speed_factor": 1.0,
        "fragment_interval": 0.3,
        "seed": 1234,
        "parallel_infer": True,
        "repetition_penalty": repetition_penalty,
        "return_fragment": False,
        "streaming_mode": False,
    }

    with _inference_lock, torch.inference_mode():
        outputs = list(_load_tts().run(inputs))
    if not outputs:
        raise RuntimeError("GPT-SoVITS returned no audio.")
    sample_rate, audio = outputs[-1]
    return int(sample_rate), _shift_pitch(audio, int(sample_rate), pitch_semitones)


with gr.Blocks(title="闲聊花花中文语音") as demo:
    gr.Markdown(
        """
        # 闲聊花花中文语音
        输入中文文字，使用 GPT-SoVITS v2ProPlus 模型在 CPU 上生成闲聊花花风格语音。

        首次生成需要下载并加载模型，耗时会明显更长。请勿用于冒充真实人物或侵权用途。
        """
    )
    text = gr.Textbox(
        label="文字",
        value=DEFAULT_TEXT,
        lines=4,
        max_lines=6,
        placeholder="请输入 120 个字符以内的中文内容",
    )
    with gr.Accordion("生成参数", open=False):
        pitch_semitones = gr.Slider(
            -3.0,
            3.0,
            value=0.5,
            step=0.25,
            label="音高（半音）",
            info="自然重采样移调；升高时语速会略快。+0.5 半音约快 3%，不改变中文声调规则。",
        )
        temperature = gr.Slider(0.1, 1.2, value=0.6, step=0.05, label="Temperature")
        repetition_penalty = gr.Slider(
            1.0, 1.8, value=1.35, step=0.05, label="Repetition penalty"
        )
    generate = gr.Button("生成语音", variant="primary")
    audio = gr.Audio(label="生成结果", type="numpy")
    generate.click(
        fn=synthesize,
        inputs=[text, pitch_semitones, temperature, repetition_penalty],
        outputs=audio,
        concurrency_limit=1,
    )


if __name__ == "__main__":
    demo.queue(max_size=8, default_concurrency_limit=1).launch(show_error=True)
