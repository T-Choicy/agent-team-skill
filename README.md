# agent-team-skill

适用于 Codex 的手动多 agent 协作技能，包含工程物理五角色集群和经典三角色集群。

## 调用

```text
/agent-physics 具体任务
/agent-normal 具体任务
```

也可以明确调用 `$agent-team-skill`，并指定集群。两个集群默认休眠；每轮依次询问各角色的模型与推理强度，全部实际确认后才派遣。默认建议 `gpt-6-astra / ultra`；模型须由所使用的 Codex 环境支持。

## 安装

### Codex marketplace（推荐）

在支持 `codex plugin` 的 Codex CLI 中执行：

```text
codex plugin marketplace add T-Choicy/agent-team-skill
codex plugin add agent-team-skill@t-choicy-skills
```

这会一起安装三个技能。marketplace 是本仓库提供的分发源，不代表已上架 OpenAI 官方公共市场。安装包仅包含技能与本地证据脚本，不注册 MCP 服务、侧栏面板、全局 agent 类型或后台进程；安装本身不唤醒集群。

安装后重新加载 Codex 技能，或重启 Codex。若已手动安装同名技能，应只启用其中一种安装来源，避免重复入口；安装包不会自动删除已有技能。

marketplace 安装的技能会带包名前缀。可在技能菜单中选择 `agent-physics`、`agent-normal`，也可以明确引用完整名称 `$agent-team-skill:agent-physics`、`$agent-team-skill:agent-normal` 或 `$agent-team-skill:agent-team-skill`。

更新时刷新 marketplace，再安装该包：

```text
codex plugin marketplace upgrade t-choicy-skills
codex plugin add agent-team-skill@t-choicy-skills
```

卸载 marketplace 安装的包：

```text
codex plugin remove agent-team-skill@t-choicy-skills
codex plugin marketplace remove t-choicy-skills
```

### 手动安装

将仓库 `skills/` 下的三个目录复制到用户的 Codex 技能目录（默认 `~/.codex/skills/`），保留它们的相邻目录关系。已有同名技能时先核对本地修改，再决定是否替换。重新加载技能后使用以上入口。

```text
skills/
  agent-team-skill/    主流程、八个角色、证据脚本
  agent-physics/      工程物理集群调用入口
  agent-normal/       经典集群调用入口
```

## 分工与流程

工程物理集群：Lead 管理任务、权限和验收；Architect 设计；Implementer 实现与自测；Reviewer 独立审工程；Physics Reviewer 独立审物理。

设计 → Design ID → 双设计审查 → 实施与自测 → 独立交付检查 → Snapshot 冻结 → 双线验证 → 验收。

经典集群：sentry 调查事实；debater 分析方案；laborer 实现和测试，由独立 sentry 审查。关键问题未决不进入实施。

每个文件只有一个写入负责人，设计者和实现者不自审。重大物理选择交由用户决定。修复先解冻，再修改、重冻和复审，保留历史记录。

## 证据与边界

使用 Codex 原生 collaboration 工具派遣成员，在任务工作区 `.agent-team/<run_id>/` 保存状态和证据。标准库脚本记录实际命令、退出码、原始日志和源码哈希，保存快照并检查漂移。需要 Python 3.9 或以上及支持所选模型参数的原生协作工具。

这是技能协议与本地辅助脚本，不提供可视化面板、服务端身份认证、自动审查门禁或操作系统写锁。前后哈希不能证明检查间隔内从未短暂修改后恢复。

## 自测

```text
python -B -m unittest discover -s skills/agent-team-skill/scripts -p test_evidence.py -v
```

证据脚本有 6 项自动化测试。2026-11-08 已使用两个隔离的最小真实任务，完成工程物理五角色集群和经典三角色集群的流程验证；八位角色均由用户逐项确认使用 `gpt-6.1-sol / medium`。

- 工程物理集群：实现无量纲谐振子的 velocity-Verlet 求解器，通过 7 项测试、独立工程验证及解析解、能量和二阶收敛检查，针对同一冻结快照完成双线审查和 Lead 验收。
- 经典集群：实现任务状态计数函数。初版冻结后追加检查发现字符串子类契约缺陷；保留失败，先解冻，再修订设计、修复、重冻并独立复审，修订版 10 项测试和独立检查通过后验收。

完整设计、实际角色标识、命令、退出码、输出、源码哈希、冻结副本和失败历史见 [最小真实任务验证记录](validation/2026-11-08/README.md)。这只证明该次环境与有限算例所执行的流程，不代表所有模型、宿主版本、失败分支或实际科研工程任务均已验证。
