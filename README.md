# agent-team-skill

适用于 Codex 的手动多 agent 协作技能，包含工程物理五角色集群和经典三角色集群。

## 调用

```text
/agent-physics 具体任务
/agent-normal 具体任务
```

也可以明确调用 `$agent-team-skill`，并指定集群。两个集群默认休眠；每轮依次询问各角色的模型与推理强度，全部实际确认后才派遣。默认建议 `gpt-6-astra / ultra`；模型须由所使用的 Codex 环境支持。

## 安装

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

证据脚本有自动化测试；迁移后的完整真实集群流程尚未验证。
