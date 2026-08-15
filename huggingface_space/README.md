---
title: 闲聊花花中文语音
emoji: 🌼
colorFrom: yellow
colorTo: green
sdk: gradio
sdk_version: 5.49.1
python_version: "3.10"
app_file: app.py
suggested_hardware: cpu-basic
fullWidth: false
short_description: 输入中文文字，生成闲聊花花风格语音
models:
  - richarddzh/talking-flower-voice
tags:
  - text-to-speech
  - gpt-sovits
  - chinese
---

# 闲聊花花中文语音

这是 `talkflower_zh_v2pp_strict` 的 CPU Basic Gradio 演示。运行所需的微调权重与上游通用模型备份均来自 `richarddzh/talking-flower-voice`，首次生成会下载并加载模型，之后请求会复用已加载模型。

本 Space 仅用于技术演示。请确认你拥有相关角色语音、参考音频和衍生模型的使用及分发权限。
