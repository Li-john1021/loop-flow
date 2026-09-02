# Work Log：<本轮>

```yaml
schema_version: "1.0"
log_id: log:<id>
plan_ref: plan:<id>
spec_ref: spec:<id>
cycle_status: done
summary: <只总结 Trace 已证明的事实>
units:
  - ref: WU-001
    trace_event_refs: [EVT-001]
    summary: <只总结事件已证明的事实>
reviews:
  - ref: review:<id>
    trace_event_refs: [EVT-002]
    summary: <只总结事件已证明的事实>
tests:
  - ref: test:<id>
    trace_event_refs: [EVT-003]
    summary: <只总结事件已证明的事实>
decisions:
  - ref: user-decision:<id>
    trace_event_refs: [EVT-004]
    summary: <只总结事件已证明的事实>
usage_summary:
  total_tokens: 0
  total_cost: 0
  main_context_tokens: 0
  delegated_tokens: 0
next_action: <下一步合法动作>
user_approval_required: true
```
