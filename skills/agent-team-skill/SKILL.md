---
name: agent-team-skill
description: 在用户明确调用后，管理工程物理五角色集群或经典三角色集群；逐角色确认模型、独立设计审查、授权实施、证据与冻结验收。支持 /agent-physics、/agent-normal。读取技能、普通任务和恢复历史不构成唤醒授权。
---

# Agent Team Skill

两个集群默认休眠，只使用 Codex 原生协作工具和任务工作区中的本地记录。

## 调用与确认

- `/agent-physics <任务>`：工程物理集群，依次询问 Lead、Architect、Implementer、Reviewer、Physics Reviewer。
- `/agent-normal <任务>`：经典集群，依次询问 sentry、debater、laborer。
- `$agent-team-skill` 或 `/agent-team-skill`：由用户指定集群与任务；未指定集群时先问集群，不根据任务关键词选择。
- 明确的自然语言唤醒同样有效。读取文件、修改技能、查看状态或恢复历史不触发启动。授权仅限本聊天、本轮运行和所选集群。

每次只问一个角色的模型与推理强度，等待实际回答再问下一位。默认建议 `gpt-6-astra / ultra`，预选值不是回答，不沿用上一轮选择。任务或工作区缺失时先澄清；已知信息直接使用。全部角色确认前不得创建任何集群成员。取消则不派遣，模型不支持则明确说明，不静默替换。

## 实际派遣

1. 在任务工作区建立 `.agent-team/<新 run_id>/`，记录用户任务、所选集群、工作区、角色确认、获授权文件与唯一写入负责人。run_id 每轮新建；不读取旧插件数据来获得本轮授权。
2. 使用 `collaboration.spawn_agent`，必须设置 `agent_type="default"`、`fork_turns="none"`，显式传本轮 `model` 和 `reasoning_effort`。固定角色类型的预设不能覆盖用户本轮选择。
3. 读取本技能 `roles/<角色>.toml`，把完整 `developer_instructions`、本轮任务、工作区、run_id、当前 Design/Snapshot ID、文件职责和所选模型/强度放入派遣 message。TOML 中的 model、effort、sandbox 是角色原定义；派遣采用本轮选择，不能声称 default 继承了只读 OS 沙箱。
4. 工程物理 Lead 必须实际独立派遣，原聊天只负责用户中继，不能贴上 Lead 标签冒充已切换模型。Lead 接收全部选择，按依赖安排其他角色，设计通过前 Implementer 待命。
5. 登记协作工具真实返回的 agent 路径或 ID，后续发送消息和等待使用该标识。只有工具提供 thread ID 时才记录 thread ID；不得把 task_name 或 run_id 编造为线程 ID。不把当前可见聊天、最近活动或标题当成身份依据。
6. 只读角色只检查和报告，实施者只写授权文件；每个文件只有一个写入负责人。所有写入者都须知道还有其他协作者，不覆盖他人改动。

角色文件：`roles/lead.toml`、`architect.toml`、`implementer.toml`、`reviewer.toml`、`physics_reviewer.toml`、`sentry.toml`、`debater.toml`、`laborer.toml`。只读取本轮需要的角色。

## 工程物理集群

Lead 管任务、权限、状态及验收；Architect 设计；Implementer 写授权代码和测试；Reviewer 独立审工程；Physics Reviewer 独立审物理。设计者和实现者不自审，两位审查者必须是不同的实际代理，两条审查线不能互相代替。

严格顺序：设计 → Design ID → 双设计审查 → 实施、自测 → 独立交付检查 → Snapshot 冻结 → 双线独立验证 → 验收。

- Architect 输出目标、假设、接口、文件范围、物理方案、备选和验证计划；保存设计后计算实际 SHA-256 为 Design ID。两位审查者分别针对这个 ID 记录结论，通过后才能实施。
- Lead 为授权范围逐文件分配负责人、明确任务依赖。未决关键问题阻止实施；重大物理选择提交用户决定。已有授权的例行工作持续推进，不反复索要相同授权。
- Implementer 实施并运行必要自测，证据必须包含实际命令、cwd、退出码、日志和前后源码哈希。编译通过、局部测试、设计批准各有覆盖边界。
- 独立交付检查核对完整代码、测试和配置，发现问题直接返工；交付检查通过才冻结，不为进入返工而制造通过记录。
- 冻结后两位审查者对同一 Design ID 与 Snapshot ID 独立执行验证并记录 PASS/FAIL/N/A。没有物理模型时，Physics Reviewer 明确 N/A 和理由，不宣称物理正确性。
- Lead 在版本匹配、双线结论通过且无未决事项时才验收。缺证据、身份不明、审查未执行或验证失败必须保持未验证。
- 修复先记录解冻原因，再修改、自测、交付、重冻和复审。设计变化产生新 Design ID，重新做双设计审查。旧设计、失败、日志、快照不覆盖。

## 经典集群

sentry 只读收集文件、调用链、依赖、日志与测试证据；debater 只读分析，给出推荐、置信度、关键前提、推理摘要、备选取舍和未决项，不自行派生 laborer；laborer 只负责明确授权的实现与必要测试。

证据不足时按 sentry → debater → laborer 推进；事实充足时 debater → laborer。关键问题未决不实施。审查由独立于设计者和实现者的 sentry 实例完成，可复用本轮只做调查的 sentry；上下文已污染或参与设计/实现时必须另派 sentry，沿用本轮已确认的 sentry 模型与强度。不得自行 commit、push、创建 PR 或部署。

经典集群也保留设计版本、实际测试证据、交付检查、冻结和独立最终审查，但没有工程物理集群的双物理审查结论。

## 记录与证据

开始执行前阅读 [本地记录与证据操作](references/records.md)。使用 `scripts/evidence.py` 计算 Design ID、记录实际命令、冻结文件副本并检查漂移；依赖 Python 标准库。协调者维护 run.json、追加 events.jsonl 并保存审查者各自的原始报告。原始角色指令禁止任何写文件时，该角色只执行允许的检查并返回实际输出，由协调者落盘，不能借记录证据扩大其写入权限。

技能协议由实际协作角色执行，本地辅助脚本只捕获哈希和命令证据，不是身份认证服务、自动审查门禁或文件写锁。不要伪造已卸载的插件/MCP 事件。原生协作状态是最近观察结果，不保证进程存活；前后哈希不能证明期间从未短暂修改后恢复。发现漂移必须使对应证据失效。

汇报区分已实现、已执行、已验收、未验证，代码骨架用简单文本树；状态、协作关系和任务依赖在当前聊天中报告。
