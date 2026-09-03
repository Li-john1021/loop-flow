# loop-flow resume

读取最近的 checkpoint、Plan 版本和 Trace，重新检查范围、批准、能力和外部权限，再从最近安全边界继续。无法确认状态时返回 `blocked`，不得从旧上下文猜测继续。

参数：`{{ARGS}}`
