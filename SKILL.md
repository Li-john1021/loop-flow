---
name: loop-flow
description: 用 Tier 1 三字段卡快速启动，或在一个主对话中按触发器升级并编排长程 Agent 工作。通过 Plan、Cycle Spec、有界任务、低成本实施 Agent、按代码影响串行 Review、独立测试、Trace 和 Work Log 管理代码、文本、研究及其他可验证生产任务。主 Agent 保留 Technical PM 职责和最终对账权；子 Agent 只消费有界上下文并回传结构化证据。
argument-hint: [目标或 Plan 路径]
---

# Harness Orchestration

## 定位

这是一个由主对话使用的编排 Skill，不是独立 Agent 运行时，不是项目初始化器，也不是固定工程师生成器。

用户始终在一个主对话中工作。主 Agent 承担 Technical PM 职责：澄清目标、编写 Plan、整理批注、编译 Cycle Spec、拆分任务、选择模型层级、编排子 Agent、消费审查结果、处理返工并完成最终对账。

子 Agent 的职责是执行有界工作单元、运行测试或进行独立审查。子 Agent 不拥有全局目标，不得修改批准边界，不得自己批准产物，也不得用自述代替 Evidence。

## 适用时机

使用本 Skill 的条件：

- 任务包含多个实施单元、多个责任类型、较长上下文或可能返工。
- 用户希望在一个主对话中管理实施、测试、审查和恢复。
- 需要节约主对话上下文，或希望让实施单元使用较低成本模型。
- 需要独立、异步、对抗性的质量检查。

短小且可在一次对话中完成的编辑，不强行套用完整循环；可直接执行并保留最小结果记录。

默认采用 **Tier 1**：如果目标只有一个有界单元，且没有共享接口、重要代码、返工风险、跨上下文恢复、不可逆效果或外部供应商，主 Agent 只需填写 [Tier 1 Plan](templates/PLAN-LITE.md) 的 `goal`、`acceptance`、`forbidden` 三项。Tier 1 中 Plan、Spec 和 Task Envelope 合并为一张任务卡，不要求完整 Plan、指纹或双重文书。

只有触发升级条件时才晋升为完整 Plan/Cycle Spec。晋升保留原 `plan_id`、goal、acceptance 和 forbidden，不重新编写目标。

Tier 1 的默认闭环是：一个实施 Agent 完成任务并执行 `acceptance`，一个独立于实施 Agent 的 Spec Reviewer 异步核对目标、禁止效果和实际结果，然后主 Agent 汇总结论。Tier 1 不默认执行 Code Review、独立 Test Agent 或 canonical Trace；这些能力只在 Plan 指定或升级触发器命中时启用。宿主没有独立 Reviewer 时，必须使用 `review_executor=main_degraded` 或 `review_mode=none`，并在结果中标记降级，不能写成独立审查通过。

## Tier 1 最小原则

Tier 1 只强制四条：

1. `goal`、`acceptance` 和 `forbidden` 必须清楚可读。
2. 没有实际检查或产物时不能写 `done`。
3. 不得扩大用户明确给出的范围。
4. 不可逆效果必须先取得用户明确同意。

复杂任务触发晋升后，再加载 [完整治理原则](references/full-governance.md)、[跨文件语义检查](references/semantic-checks.md) 和 [用户决策记录](references/decision-record.md)，不让低风险冷启动承担全量宪章。

## 总流程

```text
主对话澄清目标
  -> Plan 初稿
  -> 用户批注
  -> 主 Agent 整理新 Plan 版本
  -> 选择 Tier 1 或完整 Plan
  -> Schema + 语义检查
  -> 用户批准实施
  -> Tier 1：最小验收 -> 独立 Spec Review（可降级）
  -> 复杂任务：编译并冻结 Cycle Spec
  -> 评估 Git / 接口 / 并行性 / 上下文 / 模型 / 外部能力
  -> 动态分派实施 Work Unit
  -> 子 Agent 返回 Artifact / Evidence / Status / Usage
  -> 按代码影响决定 Review
       重要代码：Code Review 通过后，再做 Spec Review
       非重要代码：记录跳过理由，直接做 Spec Review
  -> Finding 驱动返工，直到审查通过或阻断
  -> 按适用性执行 compile/build
  -> 独立 Test Agent 执行单元/集成测试
  -> 主 Agent 全量 Spec 对账
  -> 晋升任务写 Trace 和 Work Log；Tier 1 默认只保留最小结果摘要
  -> 用户选择是否回溯优化
```

完整模式的两个 Review 不并行。先判断本轮代码影响：`critical/material` 必须做 Code Review；`limited/none` 可以跳过，并记录理由。重要代码只有在 Code Review `pass` 后才能启动 Spec Review；Code Review 返回 `revise` 或 `blocked` 时，立即返工或暂停，不启动 Spec Review，避免浪费 token。代码不重要时直接做 Spec Review。每个 Review 的执行者由 `review_executor` 决定：`independent_subagent` 才能声明独立审查，`manual_reviewer` 只能声明人工/外部审查，`main_degraded` 只能声明降级自检。测试默认发生在 Review 通过之后；如果 Review 发现问题，先返工并按同一顺序重新审核，不得用测试通过掩盖未处理 Finding。

## 阶段一：Plan 对话与批注

### 1. 生成初稿

先通过对话理解目标，不直接写代码。默认生成符合 [Plan Lite Schema](schemas/plan-lite.schema.json) 的 Tier 1 初稿；只有出现升级触发器时，才生成符合 [Plan Schema](schemas/plan.schema.json) 的完整 Plan，并使用 [Plan 模板](templates/PLAN.md)。完整 Plan 至少包含：

- 可观察的目标和成功定义；
- 当前问题、已有状态和来源；
- 范围内与范围外；
- 原子 Requirements；
- Deliverables；
- 可执行 Acceptance 和 Evidence 类型；
- 决策、风险、约束和未决问题；
- 执行政策：Git、工作区、接口、并行性、模型层级和上下文策略；
- 质量政策：按代码影响串行 Review、测试、构建、Trace、Work Log 和回溯；
- `approval.status=not_requested`。

Plan 初稿可以是 Markdown 人类视图，但 canonical 版本必须能转换为 JSON 并通过 Schema。

### 2. 接收用户批注

用户可以批注任意字段。完整 Plan 的批注追加到 `annotations[]`；Tier 1 可以使用可选 `annotations[]`，也可以只保留主对话摘要。每个批注都有 `open | accepted | rejected | resolved` 状态：`accepted` 表示下一版本采纳，`resolved` 表示已修改或明确答复并填写 `resolved_by`。

### 3. 整理与批准

主 Agent 只采纳状态为 `accepted` 的批注，生成递增 `plan_version`，保留旧版本和批注关系。Tier 1 的 `rework_count` 每形成一次 repair Unit 就递增，达到 2 时触发完整模式。以下任一条件不满足，必须继续规划对话：

- 所有 `must` Requirement 都有 Acceptance；
- Acceptance 有真实可执行的检查方式；
- 范围、依赖和主要风险明确；
- 没有阻断性 `unresolved`；
- 用户明确批准当前 Plan 指纹和实施范围。

用户批准后才允许进入 Tier 1 加工或完整 Cycle Spec 编译。用户没有批准时，任何子 Agent 都不得实施。Tier 1 的批准可以是主对话中的明确确认；晋升后的高风险 Plan 必须按完整批准合同处理。

## 阶段二：Cycle Spec 编译

只有 Tier 1 触发升级或用户明确要求完整治理时，才读取 [Cycle Spec 模板](templates/CYCLE-SPEC.md) 和 [Cycle Spec Schema](schemas/cycle-spec.schema.json)，从批准 Plan 编译本轮实施合同，并执行 [跨文件语义检查](references/semantic-checks.md)。单一有界 Tier 1 任务不重复生成 Plan、Spec 和 Envelope。

需要时可运行 [离线校验脚本](scripts/validate.py)；它不是运行时硬依赖，也不改变宿主的可移植 Skill 入口。

编译器允许：

- 把复合 Requirement 拆成原子 Requirement；
- 给 Work Unit、Acceptance 和 Validation Boundary 分配稳定 ID；
- 把 Requirement 连接到 Work Unit 和 Evidence；
- 将 Plan 的执行政策归一化为机器字段。

编译后必须执行 `references/semantic-checks.md` 的“编译时检查”，Schema 通过不等于引用、依赖、指纹和 Review 顺序语义通过。若复合 Requirement 被拆分，新的 `REQ-*` 必须通过 `source_refs` 追溯到批准 Plan 的原 Requirement，不得生成孤立 ID。

编译器禁止：

- 补写 Plan 没有决定的行为；
- 将 `assumed` 变成 `verified`；
- 用实现方便性改变用户范围；
- 删除无法验证的目标；
- 让 Reviewer 修改冻结 Spec。

若发现矛盾、不可验证 Acceptance、过期依赖或 Plan/Spec 不一致，返回：

```yaml
status: planning_review
reason: <具体冲突或缺口>
required_user_decision: <需要用户决定的事项>
```

## 阶段三：环境与编排评估

批准 Plan 后，不执行项目初始化，不生成永久工程师。主 Agent 先嗅探环境，再为本轮写入 `execution_policy`。可观察事实优先于用户申报：

| 评估项 | 结论 | 行为 |
|---|---|---|
| Git | `none / optional / required` | 决定是否使用 diff、branch、worktree、commit；无 Git 仍可运行 |
| 接口/协议 | `none / existing_contract / new_contract / unknown` | 共享接口先冻结 Contract Work Unit；未知则 planning review |
| 并行 | `serial / parallel_safe_units / conditional` | 仅无写路径、接口和验证依赖的单元并行 |
| 上下文 | 动态最小集合 | 主规划、实施、测试、Review 各自使用专属上下文 |
| Agent 数量 | 动态 | 一个有界单元可由一个 Agent 完成；跨责任必须分离 |
| 模型 | `frontier / balanced / economy` | 按风险、难度和可验证性分层 |
| 外部能力 | `none / provider / manual` | 网络、凭据、API 和费用单独门禁 |

不能因为“有多个任务”就自动并行。接口、Schema、共享数据、权限、迁移和发布边界默认串行。

### Tier 1 升级触发器

Tier 1 默认不加载完整合同。出现以下任一条件时，主 Agent 必须在 Work Log 记录触发器并晋升：

| 触发器 | 晋升内容 |
|---|---|
| 多于一个 Work Unit，或触碰共享接口/Schema | 完整 Work Unit 表、依赖和 Cycle Spec |
| 实际变更涉及核心行为、权限、迁移、公开 API 或发布 | 当前单元 `code_impact=critical/material`，Code Review 必做 |
| 同一问题返工达到 2 次 | 冻结 Cycle Spec、候选指纹和 repair Unit |
| 主对话需要压缩、跨上下文或恢复 | Trace、Work Log 和 checkpoint |
| 删除、迁移、资金、发布等不可逆效果 | 用户批准门和真实指纹 |
| 外部 API、凭据、网络或付费模型 | provider/data access gate |

未触发时保持 Tier 1，不为了形式补齐完整 Plan。

### 环境默认探测

在要求用户申报前，主 Agent 先读取低风险环境信号：

- 根目录存在 `.git` 或 `git rev-parse --is-inside-work-tree` 成功，则 `git_mode=optional`；否则为 `none`，除非 Plan 明确要求 Git。
- 发现 `pyproject.toml`、`package.json`、`Cargo.toml`、`go.mod`、`Makefile` 或已声明测试命令时，提出可执行 test/build 候选；不能执行时记录 `not_available`。
- 发现共享接口、Schema、迁移目录或多模块边界时，默认 `interface_mode=existing_contract`，否则 `none`；无法判断则 `unknown` 并请求用户确认。
- 宿主报告 subagent/parallel/Hook/usage 能力时才启用；没有报告时按 `serial/manual/usage_unavailable` 处理。
- 模型层级按角色默认：规划 `frontier` 或 `balanced`，有界实施 `economy`，高风险 Review `balanced` 或以上；若宿主无法选择，记录 `user_selected` 或 `unknown`。

探测只是默认值，不覆盖用户明确决定；探测结果和依据写入本轮 Trace/Work Log。

## 阶段四：Work Unit 分派与加工

主 Agent 每次只分派一个或一组明确可并行的 Work Unit。Tier 1 只有一个单元时，任务卡同时承担 Envelope；晋升后的任务使用 [Task Envelope 模板](templates/TASK-ENVELOPE.md) 和 [Task Envelope Schema](schemas/task-envelope.schema.json)。

在单元形成并明确其实际变更后，主 Agent 判断代码影响：

- `critical`：核心行为、安全/权限、共享接口或 Schema、数据迁移、不可逆写入或公开发布，`code_review_policy` 必须为 `required`；
- `material`：会改变生产行为、公共 API、主要依赖或关键测试，`code_review_policy` 必须为 `required`；
- `limited`：局部低风险实现、测试夹具、配置或文档关联代码，可以为 `required` 或 `optional`，不能为 `not_applicable`，并必须写明理由；
- `none`：本单元没有代码变更，`code_review_policy` 应为 `not_applicable`，并写明理由。

`code_impact` 与 `code_review_policy` 不匹配时，进入 `planning_review`，不能由主 Agent 自行放宽。

Task Envelope 至少给子 Agent：

- 当前 Unit、目标和 Acceptance 引用；
- 必要的 Plan/Spec/上下文引用；
- 允许访问的路径或资源；
- 禁止效果和命令；
- 模型层级和预算；
- 输出格式和停止条件。

子 Agent 只消费所需上下文，不加载完整演进叙事、全部仓库历史或无关素材。子 Agent 必须按 [Unit Result 模板](templates/UNIT-RESULT.md) 和 [Unit Result Schema](schemas/unit-result.schema.json) 回传：

- Artifact 引用和内容指纹；
- 实际命令、退出码和 Evidence；
- Requirement/Acceptance 映射；
- 状态：`pass | revise | blocked`；
- 用量：模型、层级、tokens、cost、duration（可获得时）；
- 未决问题和下一步。

模型自述、空的 `RESULT.json`、静态最终 JSON 或聊天中的“完成了”都不能单独形成成功 Evidence。

## 阶段五：按风险串行 Review（仅完整模式）

实施单元完成后，主 Agent 按已记录的单元代码影响发起独立 Review。`critical/material` 代码必须 Code Review；`limited/none` 可以省略 Code Review，但必须在 Trace/Work Log 中记录判断依据。即使省略 Code Review，只要本轮仍需要质量审查，Spec Review 仍然执行。

### Review A：Code Review（条件必做）

当 `code_review_policy=required` 时，先检查实际代码变更、架构边界、接口、权限、危险命令、并发、错误路径和回滚。它不能修改实现，不能降低阈值，不能自行批准。只有 `pass` 才能进入 Spec Review。

Code Review 的 `revise` 或 `blocked` 是短路结果：不得启动 Spec Review。主 Agent 只能保留报告、建立有界返工或进入 `blocked/planning_review`。

### Review B：Spec Review

Code Review 通过后，或代码影响为 `limited/none` 且已记录跳过理由时，逐项核对 Plan、冻结 Spec、Requirement、Acceptance、Artifact、Evidence、Trace 和 Work Log。它必须识别：

- 缺少实现或证据的 Requirement；
- 不可执行或不能证明目标的 Acceptance；
- 越过批准范围的变更；
- 自审、自测、自批或一次性状态伪造；
- 失败结果被包装成成功；
- 主对话重新吸收过多实施细节；
- 若宿主或 Plan 声明可提供 usage，则检查模型层级、token 和成本记录是否缺失或不可信；宿主未提供 usage 时记录 `usage_unavailable`，不把该事实本身算作 Finding。

Code Review 和 Spec Review 使用不同上下文和不同身份。Review 报告必须使用 [Review Report Schema](schemas/review-report.schema.json)，包含 finding、严重性、证据、根因假设、置信度、路由和 `next_cycle_brief`。当 Code Review 被跳过时，必须在 Spec Review 报告中引用跳过理由。没有独立子 Agent 时，`review_executor` 必须降为 `manual_reviewer` 或 `main_degraded`；后者只能记录降级自检，不能声称 independent。

## 阶段六：返工、构建与独立测试（完整模式或 Plan 明确要求时）

### 返工

任一 Review 返回 `revise`：

1. 保留当前候选和审查报告；
2. 把每个 Finding 转成有界 repair Work Unit；
3. 只修复有 Evidence 支持的问题；
4. 生成新候选；
5. 重要代码先使用新的 clean-context Code Reviewer；Code Review 通过后再使用新的 clean-context Spec Reviewer。代码不重要时只重新执行 Spec Review。

不得在审查进行时修改候选，不得重复使用同一个 Reviewer，不得删除失败审计。

### 构建/编译

按条件的 Review 通过后，依据 Plan 的 `build_mode`：

- `required`：必须执行并保存 build/compile Evidence；
- `when_applicable`：由主 Agent 判断是否适用并记录理由；
- `not_applicable`：记录不适用原因。

### 独立测试

Review 通过、构建步骤完成后，由独立 Test Agent 执行 [Test Report Schema](schemas/test-report.schema.json) 要求的单元或集成测试。测试 Agent：

- 不参与实施和 Review；
- 读取当前候选、批准 Spec 和测试入口；
- 至少覆盖一条成功路径，以及一条失败/拒绝路径（适用时）；
- 记录命令、工作目录、退出码、通过/失败数量和实际状态变化；
- 不修改生产实现或替自己放行；
- 测试不可用时返回 `not_available`，不能伪造通过。

测试失败时建立 repair Unit；测试通过不代表产品自动完成，还必须经过主 Agent 的全量 Spec 对账和用户决定。

## 阶段七：最终对账、Trace 与 Work Log（完整模式或触发 Trace 时）

完整模式下，主 Agent 在结束前执行 `references/semantic-checks.md` 的“周期结束检查”，并检查：

- 每个 Requirement 是否有 Acceptance 和实际 Evidence；
- Code Review（如要求）是否先通过，且 Spec Review 是否在其后串行通过；
- Review 是否为独立上下文且无未处理 Finding；
- 构建和独立测试是否与当前候选指纹一致；
- 禁止效果是否未发生；
- Plan、Spec、Trace、Work Log 和报告是否一致；
- 是否存在 `planning_review`、`blocked`、`not_available` 或未批准外部能力。

写入 [Trace Event Schema](schemas/trace-event.schema.json) 约束的最小事件：

```text
plan_drafted
plan_annotated
plan_reconciled
plan_approved
spec_frozen
unit_dispatched
unit_completed | unit_failed | unit_blocked
review_started | review_completed
repair_created
build_completed | build_not_applicable
test_completed | test_not_available
cycle_reconciled
user_decision
```

Trace 保存引用、指纹、状态、用量和退出码，不默认保存完整 prompt、推理或 transcript。事件 ID 使用 `EVT-` 加任意长度的十进制序号，并在周期或工作区命名空间中保持唯一。无法计算指纹时写入 `fingerprint_status=unavailable`，不得伪造哈希。Work Log 是给用户看的确定性摘要，不能添加 Trace 不存在的事实。完整模式的 Work Log 必须符合 [Work Log Schema](schemas/work-log.schema.json)；Tier 1 默认只保留最小摘要，发生晋升触发器后才启用完整 Trace/Work Log。

Tier 1 只需保留最小结果摘要：任务卡、实际验收观察、Spec Review 结论、未决问题和用户决定。若发生上下文丢失、第二次返工、不可逆效果或用户要求追溯，立即晋升完整模式并开始写 canonical Trace。

指纹不是由 Agent 心算或手填。只有升级触发器要求指纹时，使用宿主可执行的命令计算；以下是 JSON Plan 的 POSIX 写法：

```bash
python -c "import json,hashlib,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); d.pop('approval',None); d.pop('plan_fingerprint',None); print('sha256:'+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest())" plan.json
```

Windows PowerShell 使用相同 Python 命令即可。命令不可执行时，记录 `fingerprint_status=unavailable`，不得填写看似合法的假值；只有 Plan 明确要求指纹的路径才因此进入 `blocked`。

默认存储根目录为当前工作区的 `.loop-flow/`；没有写权限时由用户指定受保护目录，并在 Work Log 记录。建议布局：

```text
.loop-flow/
  plans/       # Plan 版本与批注
  cycles/      # 冻结 Cycle Spec（仅晋升后）
  units/       # Task Envelope 与 Unit Result
  reviews/     # Code/Spec Review 报告
  tests/       # 独立 Test Agent 报告
  trace/       # 追加式 Trace 事件
  work-log/    # 面向用户的摘要
```

## 阶段八：可选回溯与 Skill 优化

周期完成后询问用户是否回溯。只有用户同意才启动 Harness Engineer / SkillOpt 分析：

- Plan 是否过大或拆分错误；
- 哪些上下文可以留在子 Agent 而不回到主对话；
- 哪些任务可降低模型层级；
- 哪些 Review Finding 可以前置到 Schema、Task Envelope 或提示词；
- 哪些编排策略、接口或测试造成了返工；
- Trace 是否足以解释成本和质量。

回溯只能产生 `next_cycle_brief` 或待批准的 Skill/Workflow patch。不能自动修改当前生产 Skill、Plan、Spec 或阈值。SkillOpt 候选必须通过 held-out、对抗测试和用户批准后才能发布；发布时必须保留上一生产版本，定义失败触发条件，并在用户批准后才能执行回滚。回滚写入 `optimization_rolled_back` Trace 事件，旧版本不得删除。

## 宿主适配

### Codex

- 主对话加载本 Skill；
- 使用 Codex 原生 subagent/并行能力时，每次分派携带 Task Envelope；
- 子 Agent 只回传 Unit Result，不把完整过程灌回主对话；
- 不支持子 Agent 时自动退化串行，并记录能力缺失。

### Claude Code

- 主对话加载同一份本 Skill；
- 使用 Claude Code 原生 Agent/Skill 能力分派实施、Review 和 Test；
- Hook 是可选增强，不能假设 Hook 已安装或可强制；
- 无可强制 Hook 时，仍通过文档、Schema 和独立 Agent 完成治理；
- 不支持子 Agent 时退化串行/人工路径。

### 其他宿主

Pi、Zed、Qoder 或其他 Coding Agent 只需实现“读取 Skill、创建有界子任务、收集结构化回传”三个能力即可接入。没有这些能力时，主 Agent 必须明确报告 `serial/manual` 退化，不得声称并行或自动审查。

## 结束状态

本 Skill 只能以以下状态结束：

- `done`：Tier 1 任务完成最小验收，或完整 Plan/Spec 全量对账、所需的 Code/Spec Review 按顺序通过、适用的构建和独立测试均通过，且用户批准结束；
- `revise`：有证据支持的实现、审查或测试缺口，可在当前授权内返工；
- `planning_review`：Plan/Spec/Acceptance/依赖需要用户决策；
- `blocked`：外部权限、凭据、能力、环境或安全边界阻断，当前授权内无法继续；
- `not_available`：按 Plan 明确允许不执行某项验证，并已记录原因。不得把它写成 `done`。
