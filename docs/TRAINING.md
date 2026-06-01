# 训练流程：从碎片化中文语音到 GPT-SoVITS TTS 模型

这套流程以闲聊花花中文语音包为例，但设计目标是通用的：把分散、短句、来源结构不完全统一的中文语音素材整理成 GPT-SoVITS 可训练数据，并固化为可重复执行的阶段脚本。

本项目默认使用的原始语音压缩包为 `smbw_voice.zip`，来源记录：

| 项目 | 来源 |
| --- | --- |
| B站视频 | `https://www.bilibili.com/video/BV1jH4y127Lz/` |
| 原始 mp3 zip | `https://splatack-r2.qwp.moe/nintendo/smbw_voice.zip` |
| 提供者 | B站用户 Splatack |

## 阶段总览

| 阶段 | 脚本 | 作用 |
| --- | --- | --- |
| 01 | `scripts\stage-01-prepare-data.ps1` | 解压中文语音、ASR 标注、清理短文本和不适合训练的片段 |
| 02 | `scripts\stage-02-format-dataset.ps1` | 生成 GPT-SoVITS 训练所需的文本、HuBERT、语义 token、说话人向量等中间文件 |
| 03 | `scripts\stage-03-train-sovits.ps1` | 训练 SoVITS 声学/声码器侧权重 |
| 04 | `scripts\stage-04-train-gpt.ps1` | 训练 GPT 语义侧权重 |
| 05 | `scripts\stage-05-test-model.ps1` | 使用最新权重生成测试语音 |
| 总控 | `scripts\train-all.ps1` | 串联执行完整流程 |

## 阶段 01：数据清理和准备

```powershell
.\scripts\stage-01-prepare-data.ps1 `
  -ZipPath "C:\Users\richard\Downloads\smbw_voice.zip" `
  -OutputRoot ".\data\smbw_zh_train"
```

当前闲聊花花数据的默认清理规则：

1. 只抽取 `CNzh` 和 `TWzh`。
2. 生成 GPT-SoVITS 格式列表：`wav|speaker|zh|text`。
3. 丢弃中文字符少于 4 个的片段。
4. clean 列表默认排除文件名含 `VoiceOnly` 的素材。
5. strict 列表在 clean 基础上继续排除文件名含 `CommonBC` 的素材。

关键输出：

- `data\smbw_zh_train\audio`
- `data\smbw_zh_train\metadata\smbw_zh.list`
- `data\smbw_zh_train\metadata\smbw_zh_clean_v2pp.list`
- `data\smbw_zh_train\metadata\smbw_zh_strict_v2pp.list`
- 对应的 `*_dropped.json` 清理报告

## 阶段 02：格式化训练集

```powershell
.\scripts\stage-02-format-dataset.ps1 `
  -ListPath ".\data\smbw_zh_train\metadata\smbw_zh_strict_v2pp.list" `
  -AudioDir ".\data\smbw_zh_train\audio" `
  -ExpName "talkflower_zh_v2pp_strict" `
  -GpuNumbers "0"
```

关键输出位于 `logs\talkflower_zh_v2pp_strict`，包括：

- `2-name2text.txt`
- `4-cnhubert`
- `5-wav32k`
- `6-name2semantic.tsv`
- v2Pro/v2ProPlus 需要的说话人向量中间文件

## 阶段 03：训练 SoVITS

```powershell
.\scripts\stage-03-train-sovits.ps1 `
  -ExpName "talkflower_zh_v2pp_strict" `
  -Version v2ProPlus `
  -GpuNumbers "0" `
  -Epochs 10
```

默认产出目录：

- 训练日志：`logs\talkflower_zh_v2pp_strict\logs_s2_v2ProPlus`
- 权重：`SoVITS_weights_v2ProPlus`

## 阶段 04：训练 GPT

```powershell
.\scripts\stage-04-train-gpt.ps1 `
  -ExpName "talkflower_zh_v2pp_strict" `
  -Version v2ProPlus `
  -GpuNumbers "0" `
  -Epochs 18
```

默认产出目录：

- 训练日志：`logs\talkflower_zh_v2pp_strict\logs_s1_v2ProPlus`
- 权重：`GPT_weights_v2ProPlus`

## 阶段 05：测试模型

```powershell
.\scripts\stage-05-test-model.ps1 `
  -Text "你好，我是闲聊花花。今天也一起开心地冒险吧。" `
  -Output ".\outputs\talkflower_zh_v2pp_strict_latest.wav" `
  -Device cuda
```

## 总体脚本

完整重跑：

```powershell
.\scripts\train-all.ps1 `
  -ZipPath "C:\Users\richard\Downloads\smbw_voice.zip" `
  -ExpName "talkflower_zh_v2pp_strict" `
  -GpuNumbers "0"
```

如果只想从已经准备好的中间文件继续训练：

```powershell
.\scripts\train-all.ps1 `
  -ExpName "talkflower_zh_v2pp_strict" `
  -GpuNumbers "0" `
  -SkipData `
  -SkipFormat
```

## 复用到其他中文碎片语音数据

通用数据要求：

1. 每条音频 3-10 秒更适合作为参考/训练片段，过短片段建议过滤。
2. 列表格式固定为 `音频路径|说话人名|zh|文本`。
3. 对碎片化数据建议保留清理报告，方便回溯为什么丢弃某条样本。
4. 训练实验用不同 `ExpName` 隔离，例如 `my_voice_v2pp_clean`、`my_voice_v2pp_strict`。

可以直接复用 `scripts\filter-gpt-sovits-list.py` 对任何 GPT-SoVITS list 做最小中文长度和文件名规则过滤。
