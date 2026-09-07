# 本地浏览器执行器：动作、权限、截图与恢复

> 状态：verified · 更新：2026-09-06

该工程是固定策略的教学执行器，展示浏览器动作如何与批准、checkpoint、恢复和证据相连。仅操作 [fixtures/index.html](fixtures/index.html)，不需要账号、模型或远端业务数据。

## 运行

Node 22+。本次环境 Node 24.19.0、TypeScript 5.8.3、Playwright 1.55.0、Chromium 140.0.7339.16；依赖版本在 package-lock.json 固定。

```bash
cd 10-Knowledge/13-application-engineering/05-code/browser-agent-typescript
npm ci
npx playwright install --with-deps chromium
npm run build
npm test
```

浏览器首次下载需要网络，Linux 缺系统库时 `--with-deps` 可能需要系统包安装权限；已具备依赖可用 `npx playwright install chromium`。测试自身启动随机本地端口并在完成后关闭，浏览器只允许访问该 fixture origin。

## 从文章找到实现

| 文件 | 职责 | 读代码时重点看 |
|---|---|---|
| [policy.ts](src/policy.ts) | 本地 origin 与具体动作批准 | grant 来自可信宿主，绑定动作摘要 |
| [state.ts](src/state.ts) | pending/completed/failed checkpoint | 原子替换仅针对单写者，不声称分布式持久保证 |
| [actions.ts](src/actions.ts) | 填写、提交、重新观察、截图 | 在副作用前记录 pending，恢复先查动作 ID |
| [browser.test.ts](test/browser.test.ts) | 真实页面与故障注入 | 点击后 checkpoint 前中断、超时、取消、拒绝 |

2026-09-06 实际运行：3 个 E2E 测试通过，0 跳过；页面有可见内容，页面/控制台错误为空，最终 DOM 内容正确，PNG 已生成并查看。完整命令输出见[test-report.txt](artifacts/test-report.txt)。

[成功截图](artifacts/success/submit-1.png) · [恢复截图](artifacts/recovery/submit-1.png) · [恢复 checkpoint](artifacts/recovery/state.json)

恢复截图中输入框为空但记录保留，是 reload 后从 localStorage 读取已有动作的结果。恢复阶段没有再次点击创建。页面状态与 checkpoint 共同证明本夹具没有重复记录。

## 限制

这是单进程、单 Run、固定页面协议的执行器，没有语言模型决策、VLM 识别或任意网页动作。只覆盖同一浏览器存储保留时的恢复；没有验证浏览器 profile 丢失、断电持久性或多 Worker 并发。真实外部系统要有稳定业务 ID/幂等 API，不能复制这个 DOM 查询规则就宣称“恰好一次”。取消只在动作边界生效，已发出的点击必须查询结果。

对应[浏览器案例](../../03-cases/browser-agents/README.md)、[交互设计](../../01-concepts/02-human-agent-interaction.md)、[后端事件](../../01-concepts/01-backend-and-streaming.md)。
