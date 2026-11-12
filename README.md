# AnyBot 下载与包体验证

正式 macOS 安装包将在 Release 中提供。当前仓库用于分发准备和已签候选验证，尚无已发布的正式安装包。

原生 Intel 验收使用标准 `macos-15-intel` Runner，核准确 SHA256、Developer ID、双架构及空用户目录中的包内 Backend／Codex。测试只读模型账号和目录，不登录、不创建业务、不使用外装 AnyCLI；同一测试还须正常停止全部自有进程。

这项检查不代替 Google／模型真实登录、功能逐项验收、Apple 公证、Gatekeeper 或手机 TestFlight。QA 草稿 Release 不是正式公开下载。

标准公开仓库 Runner 的费用与架构依据：[GitHub 官方说明](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)。
