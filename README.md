# AnyBot

[下载 macOS 公开预览版 359](https://github.com/zjh7890/anybot-releases/releases/tag/v0.1.0-preview.359)。支持 Apple Silicon 和 Intel，安装包自带后台与官方 Codex，无需另装 AnyCLI 或 Node。

下载 DMG，将 AnyBot 拖入“应用程序”。打开后登录 Google 账号，再在设置中连接 ChatGPT 账号或 API Key。Release 附有 SHA256 校验文件。

359 已通过 Developer ID 签名、Apple 公证、App／DMG 附票和 Gatekeeper。原生 ARM（macOS 27.0.1）与 Intel（macOS 15.7.9）的空数据启动均通过；ARM 已实际完成 Google／ChatGPT 登录、首条原生回复及重开后的账号和历史保留。发布后另用未登录 HTTP 重新下载并核对原件。

当前为公开预览版，完整功能地图的逐项验收仍在进行。

已知问题：359 暂不能接收手机同步的诊断日志，手机本地记录仍保留。修复将在后继版本交付。

## 包体验证

原生 Intel 验收使用标准 `macos-15-intel` Runner，核准确 SHA256、Developer ID、双架构及空用户目录中的包内 Backend／Codex。测试只读模型账号和目录，不登录、不创建业务、不使用外装 AnyCLI；同一测试还须正常停止全部自有进程。

这项检查不代替 Google／模型真实登录、功能逐项验收、Apple 公证、Gatekeeper 或手机 TestFlight。QA 草稿 Release 与上方公开下载分开保留。

标准公开仓库 Runner 的费用与架构依据：[GitHub 官方说明](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)。
