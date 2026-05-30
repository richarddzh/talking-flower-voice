# 上传到 ModelScope

你确认拥有相关语音素材和模型权重的分发权限后，可以使用本仓库脚本生成 ModelScope 发布包并上传。

## 1. 生成本地发布包

```powershell
.\scripts\package-modelscope.ps1
```

输出目录：

```text
modelscope_package\talkflower_zh_v2pp_strict
```

该目录包含：

- 微调后的 GPT 权重
- 微调后的 SoVITS 权重
- 默认参考音频
- 推理依赖说明
- 推理/测速脚本
- ModelScope README 和 manifest

## 2. 登录 ModelScope

推荐在当前 shell 里设置 token，避免把 token 写入仓库：

```powershell
$env:MODELSCOPE_TOKEN = "你的 ModelScope token"
```

也可以使用你本机已有的 ModelScope 登录缓存。

## 3. 上传

创建私有模型仓库并上传：

```powershell
.\scripts\upload-modelscope.ps1 `
  -RepoId "你的命名空间/talkflower-zh-v2pp-strict" `
  -Private `
  -Create
```

如果目标仓库已存在：

```powershell
.\scripts\upload-modelscope.ps1 `
  -RepoId "你的命名空间/talkflower-zh-v2pp-strict"
```

## 4. 注意事项

1. 不要把 ModelScope token 写入任何文件或提交到 git。
2. 如果目标是公开仓库，请确认你拥有原始音频和衍生模型的公开分发权限。
3. 上传包只包含本项目推理资产；运行时仍需要 GPT-SoVITS 代码和 BERT/CNHuBERT/G2PW 等开源预训练资产。
