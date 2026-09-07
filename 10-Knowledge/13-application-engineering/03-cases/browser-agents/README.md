# Browser Agent：提交之后中断，恢复时如何不重复

> 状态：draft · 更新：2026-09-06

这是本库原创的本地浏览器案例。固定策略向任务板写入“Read the source paper”，运行真实 Chromium、DOM 动作与截图，不调用语言模型，也不访问真实业务网站。完成证据见[工程与运行记录](../../05-code/browser-agent-typescript/README.md)。

## 任务与动作

执行器先按输入框的 label 填写，再执行需要 grant 的提交动作。批准绑定动作摘要；改标题或动作 ID 后旧批准失效。网页没有网络业务接口，记录保存在浏览器 localStorage。执行器只允许测试启动的 `http://127.0.0.1:端口`，浏览器请求也受同源路由限制。

## 故障窗口与恢复依据

我们故意在按钮点击成功、记录出现在页面之后抛出中断，此时本地 checkpoint 仍是 pending。恢复时重载页面，从原 localStorage 得到已创建记录，使用动作 ID 查找它；找到后记录完成并截图，最终列表仍只有一条。它说明恢复端需要查外部事实，而不只是重新运行上一行代码。

| 测试 | 实际检查 |
|---|---|
| 成功路径 | 页面标题、输入、提交、最终文本、PNG 文件 |
| 权限与参数 | 外站 URL 拒绝、无 grant 拒绝、改内容后旧 grant 无效 |
| 崩溃恢复 | pending checkpoint、页面 reload、记录数仍为 1 |
| 暂时不可操作 | 禁用输入框使动作超时，恢复控件后同动作成功 |
| 取消 | 已取消信号阻止下一步，列表无提交 |
| 浏览器错误 | 全程收集 pageerror 和 console.error，必须为空 |

截图用于人审，最终记录数量和内容由 DOM 断言验收。[恢复后的截图](../../05-code/browser-agent-typescript/artifacts/recovery/submit-1.png)中输入框已清空，任务记录仍保留，符合页面重载后的语义。

## 哪些结论不能外推

恢复只覆盖同一浏览器存储仍在、单执行器、固定页面协议的情况。真实网站如果没有稳定业务 ID 或幂等接口，不能靠猜测 DOM 保证不重复；浏览器 profile 丢失、并发 Worker、系统断电写盘持久性也未在本例验证。任何真实账号操作都需要独立权限与集成测试。依据：[Playwright actionability](https://playwright.dev/docs/actionability)、[截图 API](https://playwright.dev/docs/screenshots)。
