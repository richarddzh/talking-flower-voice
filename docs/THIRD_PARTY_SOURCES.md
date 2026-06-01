# 第三方来源与本仓库修改方式

本仓库是在 GPT-SoVITS 的代码基础上整理出的“闲聊花花中文 TTS 语音包训练工程”。当前保持可工作状态，采用 **copy 第三方源码到本仓库** 的方式，而不是 git submodule。

## 为什么保持 copy 方式

当前仓库已经能完成数据准备、训练、推理和测速。为了避免把可工作的本地训练状态迁移到 submodule 时引入额外风险，本轮规范化继续保留 copy 方式，并通过文档明确来源和本仓库自有改动边界。

## 主要第三方来源

| 路径 | 来源/说明 |
| --- | --- |
| `GPT_SoVITS`、`webui.py`、`api.py`、`api_v2.py` 等 | GPT-SoVITS 项目源码，来源仓库：`https://github.com/RVC-Boss/GPT-SoVITS` |
| `GPT_SoVITS\BigVGAN` | BigVGAN 相关代码，随 GPT-SoVITS 依赖引入 |
| `tools\AP_BWE_main` | AP-BWE 相关代码，随 GPT-SoVITS 依赖引入 |
| `tools\asr`、`tools\uvr5` 等 | GPT-SoVITS 工具链相关代码 |
| `data\smbw_voice_raw`、`data\smbw_zh_train` | 原始训练语音来自 B站用户 Splatack 提供的 `smbw_voice.zip`，来源视频：`https://www.bilibili.com/video/BV1jH4y127Lz/`，zip：`https://splatack-r2.qwp.moe/nintendo/smbw_voice.zip` |

第三方许可证文件保留在对应目录；顶层 `LICENSE` 和第三方目录下的 license 文件应随源码一起保留。

## 本仓库自有改动原则

1. 不把训练工程需求散落到第三方核心代码里。
2. 项目自有逻辑集中放在 `scripts` 和 `docs`。
3. 模型、数据、日志、测试输出使用明确目录隔离：
   - `data`
   - `logs`
   - `GPT_weights_v2ProPlus`
   - `SoVITS_weights_v2ProPlus`
   - `outputs`
4. 如果未来必须修改第三方核心代码，需要在本文档中记录：
   - 修改路径
   - 修改原因
   - 与上游行为的差异
   - 是否可以回收成上游 PR 或独立 patch

## 当前规范化新增/维护的项目自有入口

| 路径 | 作用 |
| --- | --- |
| `scripts\init-venv.ps1` | 创建本地 Python 虚拟环境并安装依赖 |
| `scripts\download-modelscope-model.ps1` | 从 ModelScope 下载预训练模型和中文 ASR 模型 |
| `scripts\prepare-smbw-training.ps1` | 准备 SMBW 中文素材和 ASR list |
| `scripts\stage-01-prepare-data.ps1` | 数据准备与清理 |
| `scripts\stage-02-format-dataset.ps1` | GPT-SoVITS 训练集格式化 |
| `scripts\stage-03-train-sovits.ps1` | SoVITS 训练 |
| `scripts\stage-04-train-gpt.ps1` | GPT 训练 |
| `scripts\stage-05-test-model.ps1` | 模型推理测试 |
| `scripts\train-all.ps1` | 总体训练流程 |
| `scripts\infer-talkflower.ps1` | 最新模型推理 |
| `scripts\benchmark-talkflower.ps1` | GPU/CPU 推理测速 |
| `docs\USAGE.md` | 使用和测速说明 |
| `docs\TRAINING.md` | 分阶段训练说明 |

## 后续维护建议

如果需要同步上游 GPT-SoVITS，建议先在临时目录对比上游差异，再把必要更新合入当前 copy 目录；不要直接覆盖本仓库已有数据、日志、模型和脚本。
