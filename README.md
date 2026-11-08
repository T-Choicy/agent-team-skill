# agent-team-skill

用于 Codex 的手动多 agent 协作技能，提供工程物理集群和经典集群。需要支持原生多 agent 协作的 Codex 环境；本地证据脚本需要 Python 3.9 或以上。

## 安装

```text
codex plugin marketplace add T-Choicy/agent-team-skill
codex plugin add agent-team-skill@t-choicy-skills
```

安装后重新加载技能或重启 Codex。若之前手动安装了同名技能，只启用一种安装来源，避免重复入口。

## 使用

在技能菜单中选择相应入口并说明任务：

```text
/agent-physics 检查数值程序的能量守恒，并完成必要修复和验证。
/agent-normal 排查程序启动失败的原因并修复。
```

marketplace 安装的完整技能名称为 `$agent-team-skill:agent-physics`、`$agent-team-skill:agent-normal`。也可以调用 `$agent-team-skill:agent-team-skill` 后明确指定集群。

- 工程物理集群：Lead 管任务与验收，Architect 设计，Implementer 实现，Reviewer 独立审工程，Physics Reviewer 独立审物理。
- 经典集群：sentry 调查，debater 分析方案，laborer 实现，由独立 sentry 审查。

两个集群默认休眠。每次调用都按角色顺序询问模型与推理强度，收到全部回答后才派遣；默认建议 `gpt-6-astra / ultra`，实际模型须受当前环境支持。重大物理选择交由用户决定。

任务记录与验证证据保存在任务工作区的 `.agent-team/` 中，无需另行下载验收材料。安装包不含面板或 MCP 后台。

## 更新

```text
codex plugin marketplace upgrade t-choicy-skills
codex plugin add agent-team-skill@t-choicy-skills
```

## 卸载

```text
codex plugin remove agent-team-skill@t-choicy-skills
codex plugin marketplace remove t-choicy-skills
```
