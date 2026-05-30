import argparse
import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
SOVITS_WEIGHT_ROOT = {
    "v1": "SoVITS_weights",
    "v2": "SoVITS_weights_v2",
    "v3": "SoVITS_weights_v3",
    "v4": "SoVITS_weights_v4",
    "v2Pro": "SoVITS_weights_v2Pro",
    "v2ProPlus": "SoVITS_weights_v2ProPlus",
}
GPT_WEIGHT_ROOT = {
    "v1": "GPT_weights",
    "v2": "GPT_weights_v2",
    "v3": "GPT_weights_v3",
    "v4": "GPT_weights_v4",
    "v2Pro": "GPT_weights_v2Pro",
    "v2ProPlus": "GPT_weights_v2ProPlus",
}


def bool_arg(value: str) -> bool:
    return str(value).lower() in {"1", "true", "yes", "y"}


def sovits_config(args: argparse.Namespace) -> None:
    base_config = "s2.json" if args.version not in {"v2Pro", "v2ProPlus"} else f"s2{args.version}.json"
    config_path = REPO_ROOT / "GPT_SoVITS" / "configs" / base_config
    data = json.loads(config_path.read_text(encoding="utf-8"))
    exp_dir = REPO_ROOT / "logs" / args.exp_name

    if not args.is_half:
        data["train"]["fp16_run"] = False
        args.batch_size = max(1, args.batch_size // 2)

    data["train"]["batch_size"] = args.batch_size
    data["train"]["epochs"] = args.epochs
    data["train"]["text_low_lr_rate"] = args.text_low_lr_rate
    data["train"]["pretrained_s2G"] = args.pretrained_s2g
    data["train"]["pretrained_s2D"] = args.pretrained_s2d
    data["train"]["if_save_latest"] = args.save_latest
    data["train"]["if_save_every_weights"] = args.save_every_weights
    data["train"]["save_every_epoch"] = args.save_every_epoch
    data["train"]["gpu_numbers"] = args.gpu_numbers
    data["train"]["grad_ckpt"] = args.grad_ckpt
    data["train"]["lora_rank"] = args.lora_rank
    data["model"]["version"] = args.version
    data["data"]["exp_dir"] = str(exp_dir)
    data["s2_ckpt_dir"] = str(exp_dir)
    data["save_weight_dir"] = SOVITS_WEIGHT_ROOT[args.version]
    data["name"] = args.exp_name
    data["version"] = args.version

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


def gpt_config(args: argparse.Namespace) -> None:
    base_config = "s1longer.yaml" if args.version == "v1" else "s1longer-v2.yaml"
    config_path = REPO_ROOT / "GPT_SoVITS" / "configs" / base_config
    data = yaml.load(config_path.read_text(encoding="utf-8"), Loader=yaml.FullLoader)
    exp_dir = REPO_ROOT / "logs" / args.exp_name

    if not args.is_half:
        data["train"]["precision"] = "32"
        args.batch_size = max(1, args.batch_size // 2)

    data["train"]["batch_size"] = args.batch_size
    data["train"]["epochs"] = args.epochs
    data["pretrained_s1"] = args.pretrained_s1
    data["train"]["save_every_n_epoch"] = args.save_every_epoch
    data["train"]["if_save_every_weights"] = args.save_every_weights
    data["train"]["if_save_latest"] = args.save_latest
    data["train"]["if_dpo"] = args.dpo
    data["train"]["half_weights_save_dir"] = GPT_WEIGHT_ROOT[args.version]
    data["train"]["exp_name"] = args.exp_name
    data["train_semantic_path"] = str(exp_dir / "6-name2semantic.tsv")
    data["train_phoneme_path"] = str(exp_dir / "2-name2text.txt")
    data["output_dir"] = str(exp_dir / f"logs_s1_{args.version}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build GPT-SoVITS training configs without launching the WebUI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sovits = subparsers.add_parser("sovits")
    sovits.add_argument("--version", default="v2ProPlus", choices=list(SOVITS_WEIGHT_ROOT))
    sovits.add_argument("--exp-name", required=True)
    sovits.add_argument("--batch-size", type=int, default=4)
    sovits.add_argument("--epochs", type=int, default=10)
    sovits.add_argument("--text-low-lr-rate", type=float, default=0.4)
    sovits.add_argument("--save-every-epoch", type=int, default=5)
    sovits.add_argument("--gpu-numbers", default="0")
    sovits.add_argument("--pretrained-s2g", default="GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth")
    sovits.add_argument("--pretrained-s2d", default="GPT_SoVITS/pretrained_models/v2Pro/s2Dv2ProPlus.pth")
    sovits.add_argument("--save-latest", type=bool_arg, default=True)
    sovits.add_argument("--save-every-weights", type=bool_arg, default=True)
    sovits.add_argument("--grad-ckpt", type=bool_arg, default=False)
    sovits.add_argument("--lora-rank", type=int, default=32)
    sovits.add_argument("--is-half", type=bool_arg, default=False)
    sovits.add_argument("--output", required=True)
    sovits.set_defaults(func=sovits_config)

    gpt = subparsers.add_parser("gpt")
    gpt.add_argument("--version", default="v2ProPlus", choices=list(GPT_WEIGHT_ROOT))
    gpt.add_argument("--exp-name", required=True)
    gpt.add_argument("--batch-size", type=int, default=2)
    gpt.add_argument("--epochs", type=int, default=18)
    gpt.add_argument("--save-every-epoch", type=int, default=6)
    gpt.add_argument("--pretrained-s1", default="GPT_SoVITS/pretrained_models/s1v3.ckpt")
    gpt.add_argument("--save-latest", type=bool_arg, default=True)
    gpt.add_argument("--save-every-weights", type=bool_arg, default=True)
    gpt.add_argument("--dpo", type=bool_arg, default=False)
    gpt.add_argument("--is-half", type=bool_arg, default=False)
    gpt.add_argument("--output", required=True)
    gpt.set_defaults(func=gpt_config)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
