# 使用说明：闲聊花花中文 TTS 语音包

本仓库当前的最新版模型是基于 GPT-SoVITS v2ProPlus 训练的 `talkflower_zh_v2pp_strict`。它的直接目标是生成任天堂游戏角色“闲聊花花”的中文语音包；同时，这套脚本也可以复用到其他“碎片化中文语音素材训练 TTS 模型”的任务中。

## 环境安装

推荐 Windows 10/11、Python 3.12、NVIDIA GPU。CPU 可以推理但速度明显慢，训练建议使用 GPU。

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\init-venv.ps1
.\scripts\download-modelscope-model.ps1 -DownloadChineseAsr
```

安装后激活环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 最新模型文件

默认推理脚本使用：

| 类型 | 路径 |
| --- | --- |
| GPT | `GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt` |
| SoVITS | `SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth` |
| 参考音频 | `data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3` |
| 参考文本 | `只有被选中的人才能得到璀璨的光芒。` |

`outputs\talkflower_zh_v2pp_strict_ref05100_conservative.wav` 是当前保留的最新版示例输出。脚本默认参考音频使用 3-10 秒范围内的 `Course_051_00`，这是 GPT-SoVITS 推理入口对参考音频长度的要求；历史示例名中的 `ref05100` 仍作为已有测试结果保留。

## 生成语音

GPU 推理：

```powershell
.\scripts\infer-talkflower.ps1 `
  -Text "你好，我是闲聊花花。今天也一起开心地冒险吧。" `
  -Output ".\outputs\talkflower_latest.wav" `
  -Device cuda
```

CPU 推理：

```powershell
.\scripts\infer-talkflower.ps1 `
  -Text "你好，我是闲聊花花。今天也一起开心地冒险吧。" `
  -Output ".\outputs\talkflower_latest_cpu.wav" `
  -Device cpu
```

## 推理测速

分别测试 GPU 和 CPU：

```powershell
.\scripts\benchmark-talkflower.ps1 -Warmup 1 -Runs 3
```

只测 GPU：

```powershell
.\scripts\benchmark-talkflower.ps1 -SkipCpu -Warmup 1 -Runs 3
```

只测 CPU：

```powershell
.\scripts\benchmark-talkflower.ps1 -SkipGpu -Warmup 1 -Runs 3
```

测速结果会写入：

- `outputs\benchmark\talkflower_cuda.json`
- `outputs\benchmark\talkflower_cpu.json`

当前机器实测结果：

| 设备 | 平均耗时 | 平均生成音频时长 | 平均 RTF | 说明 |
| --- | ---: | ---: | ---: | --- |
| NVIDIA GeForce RTX 4070 / CUDA | 2.717 秒 | 5.120 秒 | 0.531 | 快于实时播放 |
| CPU | 5.979 秒 | 5.000 秒 | 1.196 | 慢于实时播放 |

测试命令：

```powershell
.\scripts\benchmark-talkflower.ps1 -Warmup 1 -Runs 3
```

指标说明：

- `elapsed_seconds`：单次推理耗时。
- `audio_seconds`：生成音频时长。
- `rtf`：实时率，`推理耗时 / 音频时长`，越小越快；小于 1 表示快于实时播放。

## 调参建议

当前脚本默认使用保守参数：`top_k=5`、`temperature=0.6`、`repetition_penalty=1.35`。如果声音过于保守，可以适当提高 `temperature`；如果出现重复，可以提高 `repetition_penalty` 或缩短输入文本。

关于“为什么推理还需要参考语音和参考文字”、以及大量 TTS/API service 如何降低冷启动，请阅读 [训练与推理原理简述](PRINCIPLES.md)。
