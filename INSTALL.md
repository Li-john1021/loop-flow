# 安装 loop-flow

loop-flow 是一个可移植的 Skill，不是常驻运行时。安装只需把整个目录放到宿主的 Skill 目录；不需要 Python、依赖包或项目初始化器。

## 项目级安装

在目标项目根目录执行以下命令，选择正在使用的平台：

如果父目录不存在，先创建对应的 `.<platform>/skills` 目录。

```text
# Claude Code
git clone https://github.com/Li-john1021/loop-flow.git .claude/skills/loop-flow

# Codex
git clone https://github.com/Li-john1021/loop-flow.git .codex/skills/loop-flow

# Gemini CLI
git clone https://github.com/Li-john1021/loop-flow.git .gemini/skills/loop-flow
```

也可以把仓库目录完整复制到对应路径。不要只复制 `SKILL.md`，因为 Schema、模板、参考文档和校验器是同一份 Skill 资源。

## 用户级安装

需要对所有项目生效时，将目录放到宿主的用户级 Skill 目录：

```text
<user-home>/.claude/skills/loop-flow
<user-home>/.codex/skills/loop-flow
<user-home>/.gemini/skills/loop-flow
```

项目级目录优先用于项目专属版本；用户级目录适合复用同一版本。不要同时安装同名的项目级和用户级版本，除非你明确知道宿主的优先级规则。

## 更新

Git 安装可在对应目录执行：

```text
git pull --ff-only
```

更新前保留用户对 Skill 的本地修改，或先复制到独立目录审阅。运行产物不写入 Skill 目录，而写入目标项目的 `.loop-flow/`。

## 首次 smoke check

1. 在宿主中确认 `loop-flow` 已被发现。
2. 用自然语言请求：`用 loop-flow 为“修正一个文档命令”生成 Plan。`
3. 确认主对话先生成 Plan，并把缺口写入 `annotations`，没有用户批准前不实施。

有 Python 3.9+ 时，可额外运行：

```text
python <loop-flow-root>/scripts/validate.py --root <loop-flow-root>
```

Claude Code 可直接使用 `/loop-flow`；新建顶层 Skill 目录后若未被发现，重启会话。Gemini CLI 可使用 `/skills list` 查看、`/skills reload` 重新扫描。其他宿主使用其 Skill 发现或自然语言入口。

## 可选校验器

Skill 本身不依赖 Python。只有需要离线校验 Schema、批注门、引用和指纹时，才需要 Python 3.9+：

```text
python scripts/validate.py --root <loop-flow-root>
```

需要强制标准 JSON Schema 校验时使用 `--require-jsonschema`；此模式额外需要 `jsonschema` 包。没有该环境时，必须把结果记录为结构化降级，不能声称完成完整 Schema 校验。

## 边界

- 不创建空的 `.loop-flow/` 目录；只有任务需要持久化 Plan、Cycle、Review、Test、Trace 或 Work Log 时才创建对应产物。
- 安装不会调用外部 API、读取凭据、修改用户文件或自动发布。
- 外部 API、凭据、付费模型、提交和发布仍需用户单独批准。
