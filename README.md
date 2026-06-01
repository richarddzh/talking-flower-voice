# talking-flower-voice

这个仓库的直接目标，是训练一个任天堂游戏角色“闲聊花花”的中文 TTS 语音包，并保留从数据清理、训练、推理到测速的完整过程。

更通用地说，它也是一个 **用碎片化中文语音素材训练 GPT-SoVITS TTS 模型** 的工程模板：适合把大量短句、游戏语音、角色台词或其他中文碎片音频整理成可复用的 TTS 训练流程。

## 当前状态

当前可工作的最新版模型为 `talkflower_zh_v2pp_strict`，基于 GPT-SoVITS v2ProPlus 训练。

已手动上传训练后的模型文件和原始训练数据（mp3 zip）到 ModelScope：

```text
https://www.modelscope.cn/models/richarddzh/talking-flower-voice
```

原始训练语音数据来源记录：

| 项目 | 来源 |
| --- | --- |
| B站视频 | `https://www.bilibili.com/video/BV1jH4y127Lz/` |
| 原始 mp3 zip | `https://splatack-r2.qwp.moe/nintendo/smbw_voice.zip` |
| 提供者 | B站用户 Splatack |

默认推理使用：

| 类型 | 路径 |
| --- | --- |
| GPT 权重 | `GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt` |
| SoVITS 权重 | `SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth` |
| 参考音频 | `data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3` |
| 参考文本 | `只有被选中的人才能得到璀璨的光芒。` |
| 示例输出 | `outputs\talkflower_zh_v2pp_strict_ref05100_conservative.wav` |

## 快速开始

安装环境：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\init-venv.ps1
.\scripts\download-modelscope-model.ps1 -DownloadChineseAsr
```

生成一段语音：

```powershell
.\scripts\infer-talkflower.ps1 `
  -Text "你好，我是闲聊花花。今天也一起开心地冒险吧。" `
  -Output ".\outputs\talkflower_latest.wav" `
  -Device cuda
```

分别测试 GPU 和 CPU 推理速度：

```powershell
.\scripts\benchmark-talkflower.ps1 -Warmup 1 -Runs 3
```

测速结果写入 `outputs\benchmark`。

## 训练流程

分阶段执行：

```powershell
.\scripts\stage-01-prepare-data.ps1
.\scripts\stage-02-format-dataset.ps1
.\scripts\stage-03-train-sovits.ps1
.\scripts\stage-04-train-gpt.ps1
.\scripts\stage-05-test-model.ps1
```

总体执行：

```powershell
.\scripts\train-all.ps1
```

如果已经有数据和中间特征，只想继续训练：

```powershell
.\scripts\train-all.ps1 -SkipData -SkipFormat
```

## 文档

- [使用说明](docs\USAGE.md)
- [训练流程](docs\TRAINING.md)
- [训练探索博客：从 v1 到 v2pp strict](docs\training-journey-blog.html)
- [训练与推理原理简述](docs\PRINCIPLES.md)
- [训练和推理依赖差异](docs\DEPENDENCIES.md)
- [训练/推理资产说明](docs\ASSETS.md)
- [ModelScope 发布记录](docs\MODELSCOPE.md)
- [第三方来源与本仓库修改方式](docs\THIRD_PARTY_SOURCES.md)

## 数据和产物目录

| 路径 | 说明 |
| --- | --- |
| `data` | 原始解包数据、清理后的训练列表 |
| `logs` | GPT-SoVITS 数据格式化中间文件和训练日志 |
| `GPT_weights_v2ProPlus` | GPT 侧训练权重 |
| `SoVITS_weights_v2ProPlus` | SoVITS 侧训练权重 |
| `outputs` | 推理输出、ASR 测试输出、测速报告 |

这些目录是训练过程的重要资产。清理仓库时可以删除缓存、临时下载和 Python 编译缓存，但不要删除这些目录中的原始数据、中间训练步骤、日志、模型和测试结果。

如果从 GitHub 重新 clone，需要先恢复本地训练/推理资产。详见 [训练/推理资产说明](docs\ASSETS.md)，并可用以下命令检查：

```powershell
.\scripts\check-assets.ps1
```

## 第三方代码来源

本仓库保留当前可工作的方式：直接 copy GPT-SoVITS 及其依赖源码到仓库中，而不是使用 git submodule。

主要第三方来源是：

- GPT-SoVITS：`https://github.com/RVC-Boss/GPT-SoVITS`
- BigVGAN、AP-BWE、ASR/UVR5 等相关代码随 GPT-SoVITS 工具链引入

本仓库的自有规范化工作集中在 `scripts`、`docs`、README、配置说明和训练/推理产物组织上。后续如果修改第三方核心代码，应在 `docs\THIRD_PARTY_SOURCES.md` 中记录修改路径、原因和与上游的差异。
