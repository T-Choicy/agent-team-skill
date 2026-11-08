---
name: agent-normal
description: 用户明确调用 /agent-normal 时，按 agent-team-skill 启动经典三角色集群的本轮逐角色模型确认。
---

仅当用户明确调用此入口时，选择经典集群，执行 [agent-team-skill](../agent-team-skill/SKILL.md)。仅读取此文件不构成唤醒授权。依次询问 sentry、debater、laborer 的模型与强度，全部实际回答前不创建成员。不唤醒工程物理集群。
