# AnyBot

[下载 macOS 公开预览版 364](https://github.com/zjh7890/anybot-releases/releases/tag/v0.1.0-preview.364)。支持 Apple Silicon 和 Intel，安装包自带后台与官方 Codex，无需另装 AnyCLI 或 Node。

下载 DMG，将 AnyBot 拖入“应用程序”。打开后登录 Google 账号，再在设置中连接 ChatGPT 账号或 API Key。Release 附有最终 DMG 的 SHA256 校验文件。

364 已通过 Developer ID 签名、Apple 公证、App／DMG 附票和 Gatekeeper。原生 ARM（macOS 27.0.1）与 Intel（macOS 15.7.9）的空数据启动、账号／模型接口和正常退出均通过；两种架构均实际运行包内官方 Codex，经 MCP 调用任务、Todo、模型提升及手机历史工具。工具验证使用私有本地模型测试服务。发布后另用未登录 HTTP 重新下载 DMG 与校验文件，完整字节及 SHA256 一致，附票、签名与 Gatekeeper 复核通过。

本版补齐手机诊断接收，并提供按账号隔离的来源列表、分页查询、详情和导出。Swift 原生存储至客户端传输、Host 镜像与只读工具的集成测试通过；手机 UI、Expo 桥接和真机端到端仍待验。部分旧目录保留历史会退回原生读取，其预览性能仍在后继优化。

当前为公开预览版，完整功能地图的逐项验收仍在进行。359 的真实 Google／ChatGPT 登录、首条回复与重开保留是历史基线，不作 364 新验收。

## 包体验证

[原生 Intel 验收](https://github.com/zjh7890/anybot-releases/actions/runs/43344229187)使用标准 `macos-15-intel` Runner，核准确 SHA256、Developer ID、双架构及空用户目录中的包内 Backend／Codex，再实际调用包内 MCP 工具；同一原件也在 ARM 运行。测试不使用外装 AnyCLI，不登录真实账号、不调用付费模型，结束后正常停止自有运行时，并在测试进程退出后清理私有目录。

这些检查不代替 Google／模型真实登录、功能逐项验收、Apple 公证、Gatekeeper 或手机 TestFlight。QA 草稿 Release 与上方公开下载分开保留。

标准公开仓库 Runner 的费用与架构依据：[GitHub 官方说明](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)。
