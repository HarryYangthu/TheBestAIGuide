# 工具实验

| case | ok | error | passed |
|---|---|---|---|
| search | True |  | True |
| bad_limit | False | invalid_arguments | True |
| bool_limit | False | invalid_arguments | True |
| escape | False | path_denied | True |
| missing | False | not_found | True |
| python | True |  | True |
| budget2 | True |  | True |
| budget3 | True |  | True |

本入口未执行容器；当前 Docker CLI 不可用。运行 code/run_container.py 可另外生成结果。
