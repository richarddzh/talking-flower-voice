# 训练和推理依赖差异

本仓库目前保留 GPT-SoVITS 的完整源码和训练工作区，但“训练环境”和“只做推理的运行环境”需要的东西并不完全一样。

## 结论

只支持推理时，依赖确实可以更少：

| 问题 | 推理是否需要 | 训练/数据准备是否需要 | 说明 |
| --- | --- | --- | --- |
| 微调后的 GPT 权重 | 需要 | 训练产出 | 当前默认：`GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt` |
| 微调后的 SoVITS 权重 | 需要 | 训练产出 | 当前默认：`SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth` |
| GPT-SoVITS 原始 base GPT/SoVITS 权重 | 不需要 | 需要 | 已有微调权重后，推理不再需要 `s1v3.ckpt`、`s2Gv2ProPlus.pth`、`s2Dv2ProPlus.pth` 这类训练初始化权重 |
| BERT / RoBERTa 中文模型 | 需要 | 需要 | 用于中文文本 BERT 特征，路径：`GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large` |
| CNHuBERT 模型 | 需要 | 需要 | 推理时也要从参考音频提取 prompt semantic，路径：`GPT_SoVITS\pretrained_models\chinese-hubert-base` |
| G2PWModel | 需要 | 需要 | 中文多音字/拼音前端需要，路径：`GPT_SoVITS\text\G2PWModel` |
| Chinese ASR / FunASR 模型 | 不需要 | 数据准备需要 | 只在从原始音频自动生成标注文本时使用 |
| ModelScope CLI / modelscope 包 | 不需要 | 下载模型、ASR/去噪等工具需要 | 推理部署时如果模型文件已就绪，可以不安装 |
| faster-whisper | 不需要 | 可选 ASR 需要 | 当前中文数据准备默认用 FunASR，不是推理依赖 |
| Gradio WebUI | 不需要 | 只运行 WebUI 时需要 | 命令行推理和 API service 都不需要 gradio |
| TensorBoard | 不需要 | 训练需要 | SoVITS/GPT 训练日志使用 |
| PyTorch Lightning | 当前仍需要 | 训练需要 | `TTS.py` import 了 `Text2SemanticLightningModule`，该类依赖 Lightning；若未来重构成纯推理模块，可去掉 |
| torchmetrics | 当前仍需要 | 训练需要 | `AR\models\t2s_model.py` import `MulticlassAccuracy`，推理路径也会触发 import |
| FastAPI | 不需要 | 不需要 | 只有构建 API service 时才需要 |

## 推理最小运行资产

只部署最新版闲聊花花推理，至少需要保留：

```text
GPT_SoVITS\
tools\audio_sr.py
tools\AP_BWE_main\
GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt
SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth
GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large
GPT_SoVITS\pretrained_models\chinese-hubert-base
GPT_SoVITS\text\G2PWModel
data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3
scripts\talkflower-tts.py
scripts\infer-talkflower.ps1
scripts\benchmark-talkflower.ps1
```

不需要带上：

```text
tools\asr\models
data\smbw_zh_train\metadata
logs
GPT_SoVITS\pretrained_models\s1v3.ckpt
GPT_SoVITS\pretrained_models\v2Pro\s2Gv2ProPlus.pth
GPT_SoVITS\pretrained_models\v2Pro\s2Dv2ProPlus.pth
GPT_weights_v2ProPlus\其他旧实验权重
SoVITS_weights_v2ProPlus\其他旧实验权重
```

注意：上面“不需要带上”的内容是针对“只做推理部署”。本训练仓库本身仍然应该保留 `data`、`logs`、权重和测试输出，方便复现实验。

## 推理 Python 依赖

为了比完整训练环境更轻，新增了 `requirements-inference.txt`。它保留命令行推理所需的核心依赖，去掉了 ASR、ModelScope 下载、Gradio、FastAPI、TensorBoard 等训练/工具链依赖。

安装方式示例：

```powershell
python -m venv .venv-infer
.\.venv-infer\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements-inference.txt
python -m pip install --no-deps -e .
```

如果只跑 CPU，可以安装 CPU 版 PyTorch wheel，但速度会明显慢于 GPU。

## 训练 Python 依赖

完整训练仍建议使用：

```powershell
.\scripts\init-venv.ps1
.\scripts\download-modelscope-model.ps1 -DownloadChineseAsr
```

完整训练环境需要：

1. 推理依赖。
2. PyTorch Lightning、TensorBoard、DataLoader 等训练依赖。
3. FunASR / faster-whisper / ModelScope 等数据准备和下载依赖。
4. 训练初始化用 base 权重，例如 `s1v3.ckpt`、`s2Gv2ProPlus.pth`、`s2Dv2ProPlus.pth`。
5. 原始数据、metadata、中间特征和日志目录。

## API service 部署建议

API service 不应该每个请求创建新环境或重新加载模型。推荐：

1. 用推理依赖环境部署。
2. 服务启动时加载 `TTS`、GPT 权重、SoVITS 权重、BERT、CNHuBERT。
3. 启动后做一次短文本预热。
4. 固定参考音频时，后续可以进一步缓存参考音频相关特征。
5. 请求层只负责接收文本、排队、调用常驻模型并返回 wav bytes 或文件路径。

如果 API 只服务闲聊花花单角色，不需要安装 ASR、ModelScope、Gradio、TensorBoard，也不需要原始 base GPT/SoVITS 训练初始化权重。
