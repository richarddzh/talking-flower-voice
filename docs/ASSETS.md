# 训练/推理资产说明

本仓库的代码、脚本和文档已经提交到 git。训练和推理所需的大文件资产分为两类：

1. **可重新下载的开源/第三方预训练资产**：例如 BERT、CNHuBERT、G2PW、GPT-SoVITS base weights、ASR 模型。
2. **本项目从游戏语音素材产生的资产**：例如原始/清理后的闲聊花花语音数据、训练中间特征、训练日志、微调后的 GPT/SoVITS 权重和测试输出。

第二类资产包含任天堂游戏角色语音及其衍生训练产物。它们可以在本地保留用于复现实验，但不适合直接提交到准备 push 的 GitHub 仓库公开分发。

当前已手动上传训练后的模型文件和原始训练数据（mp3 zip）到 ModelScope：

```text
https://www.modelscope.cn/models/richarddzh/talking-flower-voice
```

## clone 后如何恢复到可运行状态

### 1. 安装环境

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\init-venv.ps1
```

### 2. 下载可重新获取的预训练资产

```powershell
.\scripts\download-modelscope-model.ps1 -DownloadChineseAsr
```

只做推理时，Chinese ASR 不是必需项；但如果要完整复现数据准备流程，需要下载 ASR。

### 3. 恢复本项目本地资产

如果你拥有这些素材和模型的使用/分发权限，可以把本地资产复制回以下路径：

```text
data\smbw_zh_train
logs\talkflower_zh_v2pp_strict
GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt
SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth
outputs
```

只做推理时，至少需要：

```text
GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt
SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth
data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3
GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large
GPT_SoVITS\pretrained_models\chinese-hubert-base
GPT_SoVITS\text\G2PWModel
  - g2pW.onnx
  - POLYPHONIC_CHARS.txt
```

### 4. 检查资产是否齐全

推理检查：

```powershell
.\scripts\check-assets.ps1
```

训练检查：

```powershell
.\scripts\check-assets.ps1 -Training
```

### 5. 运行推理

```powershell
.\scripts\infer-talkflower.ps1 `
  -Text "你好，我是闲聊花花。今天也一起开心地冒险吧。" `
  -Output ".\outputs\talkflower_latest.wav" `
  -Device cuda
```

## 如果未来要提交大文件资产

仓库已加入 `.gitattributes`，为模型权重和音频文件配置了 Git LFS：

```text
*.ckpt
*.pth
*.bin
*.onnx
*.wav
*.mp3
```

如果确认拥有分发权限，可以用 Git LFS 提交相关资产：

```powershell
git lfs install
git add -f GPT_weights_v2ProPlus\talkflower_zh_v2pp_strict-e18.ckpt
git add -f SoVITS_weights_v2ProPlus\talkflower_zh_v2pp_strict_e10_s2120.pth
git add -f data\smbw_zh_train\audio\TWzh__TalkFlower_Placement_Stream__Course_051_00.mp3
git commit -m "Add authorized runtime assets"
```

如果没有明确分发权限，请不要把游戏原始语音或基于它训练出的权重 push 到公开 GitHub 仓库。
