# loop-flow approve

加载根目录 `SKILL.md`。先展示待批准的 Plan ID、版本、范围、禁止效果和必要指纹，取得用户明确确认后才记录批准。批准时按策略运行 `python scripts/validate.py --fingerprint-plan <plan.json>`；不可计算时诚实标记，不得手填哈希。

参数：`{{ARGS}}`
