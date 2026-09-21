# 权限与资源实验

| 检查 | 通过 |
|---|---|
| allowed_projection | True |
| data_scope | True |
| tool_scope | True |
| approval_gate | True |
| approval_binding | True |
| approval_accept | True |
| approval_once | True |
| budget_reserve | True |
| unknown_held | True |
| concurrency | True |
| deadline | True |
| cancel_release | True |

批准事件的来源为 experiment_fixture，是自动实验签发；没有把它记作真人批准。人工入口为 approval_cli.py。
