# Project Instructions

## GPT-SoVITS setup constraints

- Use ModelScope instead of Hugging Face for downloading GPT-SoVITS model files:
  - https://www.modelscope.cn/models/AIDub/GPT-SoVITS/summary
- Use the Aliyun PyPI mirror for Python package installation:
  - https://mirrors.aliyun.com/pypi/simple/
- If GPT-related packages require PyTorch, use the CUDA 12.8 wheels provided by the user because the machine has GPU and CUDA installed:
  - https://mirrors.aliyun.com/pytorch-wheels/cu128/torch-2.10.0+cu128-cp312-cp312-win_amd64.whl
  - https://mirrors.aliyun.com/pytorch-wheels/cu128/torchvision-0.25.0+cu128-cp312-cp312-win_amd64.whl
- Avoid Hugging Face as the primary download source unless the user explicitly changes this instruction.
- Train only from `C:\Users\richard\Downloads\smbw_voice.zip`.
- Use only the `CNzh` and `TWzh` folders from that archive because only Chinese speech is needed.
- Treat the current working directory as the git repository root and manage it like a normal Python project with `.venv`, `pyproject.toml`, and `.gitignore`.
- If large non-pip downloads are too slow locally, the fallback host is:
  - `ssh -i C:\Users\richard\.ssh\id_ed25519 richard@zhdon.japaneast.cloudapp.azure.com`
- Even when using the fallback host:
  - keep Python package installation on the local machine using the Aliyun mirror
  - prefer ModelScope for model downloads whenever the needed asset exists there
  - avoid relying on GitHub or Hugging Face unless there is no workable ModelScope path
