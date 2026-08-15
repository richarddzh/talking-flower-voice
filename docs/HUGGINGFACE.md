# Hugging Face 模型与 CPU Space 发布

本项目的 Hugging Face 发布分为两个仓库：

1. **Model repo**：保存闲聊花花微调后的 GPT/SoVITS 二进制权重、参考音频和模型清单。
2. **Space repo**：保存 Gradio 页面和 GPT-SoVITS 推理源码，使用 CPU Basic 运行。

Model repo 同时保存闲聊花花微调权重和运行所需的上游模型备份：

- `lj1995/GPT-SoVITS` 的 Chinese RoBERTa、CNHuBERT 与说话人验证模型
- `IQ-Technology/G2PWModel` 的 G2PW 模型
- Facebook FastText 的 `lid.176.bin` 语言识别模型

Space 只从你的 Model repo 下载固定副本，避免上游文件删除或变更后无法运行。Model repo README 会记录每份备份的原始仓库与路径。

## 1. 准备发布包

```powershell
.\scripts\package-huggingface.ps1 `
  -ModelRepoId "你的用户名/talking-flower-voice"
```

输出：

```text
huggingface_package\model
huggingface_package\space
```

完整模型包约 1.9 GB；Space 源码包不包含模型二进制。

## 2. 登录 Hugging Face

推荐使用 Hugging Face CLI 登录。登录信息保存在本机凭据缓存中，上传脚本会自动读取：

```powershell
hf auth login
```

如果系统尚未安装 `hf` 命令，可先安装：

```powershell
python -m pip install --upgrade huggingface_hub
```

也可以只在当前 shell 设置 `HF_TOKEN`；环境变量会覆盖登录缓存：

```powershell
$env:HF_TOKEN = "hf_..."
```

无论采用哪种方式，都不要把 token 写入脚本、配置文件或 git。

## 3. 创建并上传

```powershell
.\scripts\upload-huggingface.ps1 `
  -ModelRepoId "你的用户名/talking-flower-voice" `
  -SpaceRepoId "你的用户名/talking-flower-voice-space" `
  -Create
```

如果仓库已存在，去掉 `-Create`。脚本创建的 Model repo 和 Space 默认均为公开仓库。如需私有仓库，可加入 `-PrivateModel` 或 `-PrivateSpace`；私有模型仓库还需要在 Space Settings 中配置可读取该模型的 `HF_TOKEN` secret。

## 4. CPU Basic 行为

- Space 固定使用 CPU 和 FP32。
- 单次最多输入 120 个字符。
- Gradio 提供 `-3` 到 `+3` 半音的全局音高调节，默认 `+0.5` 半音，以缓解 strict 模型听感偏低沉的问题。它使用高质量重采样，升高音高时语速会自然略快（`+0.5` 半音约快 3%），避免保时长相位声码器产生混响/合唱感；不会改写中文声调。
- 队列并发为 1，避免多个请求同时加载/推理导致内存不足。
- 首次请求需要下载约 1.9 GB 资产并加载模型，后续请求复用内存中的模型。
- 本机 CPU 基准约为 RTF 1.20；Hugging Face CPU Basic 性能可能更低。

## 5. 权限提醒

上传或公开分享前，请确认你拥有游戏角色语音、参考音频及衍生模型权重的分发权限。
