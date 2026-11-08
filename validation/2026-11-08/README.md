# 两个集群的最小真实任务验证

日期：2026-11-08。验证前仓库提交：`d7d7fca5062b55473125e8fd16f36310e8b255f6`。技能核心文件未改动；本次新增玩具任务、验证记录并更新发布说明。

用户逐角色确认了八位成员均使用 `gpt-6.1-sol / medium`，随后才实际派遣。这里验证的是 Codex 原生协作与本地记录协议，不是旧 MCP 插件或模拟出来的角色。

| 集群 | 最小真实任务 | 最终结果 | 验收与实际证据 |
| --- | --- | --- | --- |
| 工程物理 | 无量纲 `x''=-x`，velocity-Verlet，固定初始状态 | 7 项测试、工程与物理独立验证通过，Lead 有限验收 | [验收索引](evidence/engineering/acceptance.md) · [运行记录](evidence/engineering/run.json) |
| 经典 | 统计四种任务状态，校验输入并保持输入不变 | 修订版 10 项测试、独立验证通过，协调者有限验收 | [验收索引](evidence/classic/acceptance.md) · [运行记录](evidence/classic/run.json) |

## 工程物理集群

实际路径：逐角色确认 → Lead → Architect 设计与 Design ID → 工程和物理双设计审查 → Implementer 实施和自测 → 独立交付检查 → Snapshot 冻结 → 双线独立验证 → Lead 验收。

- Design ID：`a4004d1d22ebd3c55af012fb7e10f9982c8f79ac249f2cb928d1e1575c8be441`
- Snapshot ID：`19bff99b32056818cd36a020f92463dd0428729b98164ecb8e806b1b42c1ca77`
- 初始条件：`x(0)=1, v(0)=0`；解析参照：`x=cos(t), v=-sin(t)`，能量为 `(x*x+v*v)/2`。
- 独立验证观察到约二阶收敛（误差比约 `4.0062`、`4.0015`），并检查有限步长/时长下的解析误差、能量区间及离散解析解。

具体容差、命令、数值和适用范围以 [设计](evidence/engineering/design-v1.md) 及独立审查报告为准。两个审查角色与设计、实现作者不同；父聊天没有冒充被选模型的 Lead。

## 经典集群与实际返工

实际路径：逐角色确认 → sentry 调查 → debater 设计与 Design ID → sentry 独立设计审查 → laborer 实施和自测 → 独立交付检查 → 冻结 → 独立验证 → 发现失败 → 解冻 → 设计修订及独立审查 → 修复自测 → 交付、重冻、独立复审 → 有限验收。

- 最终 Design ID：`2e33e2bad7e95f44181c71a66e49f54144d6c05aecfa9b58c72b48a1095813e9`
- 最终 Snapshot ID：`b58c8cc496e6a466d10360c9b6d244e1677721986c5514a57580c5f71422d39f`
- [v1 冻结后的实际失败](evidence/classic/frozen-v1-subclass-failure.json)：设计承诺接受字符串子类，但合法文本的不可哈希子类在字典成员检查处抛出 `TypeError`。
- v1 普通测试和普通子类检查曾通过；[随后修正的审查结论](evidence/classic/frozen-review-v1-correction.json) 保留了这一覆盖不足，没有覆盖或删除先前记录。
- [v2 设计](evidence/classic/design-v2.md) 明确把测试算例接口收紧为内置 `list` 和 `str`，有意拒绝所有子类，并增加回归检查。它不是对旧子类接受契约的通过声明，也不改变技能本身的接口。

最终的 sentry 是独立审查者；debater 的关闭建议不代替独立审查。协调者依据新快照的独立 PASS 关闭该有限任务。

## 复现算例测试

从仓库根目录运行：

```text
python -B -m unittest discover -s validation/2026-11-08/engineering -p test_oscillator.py -v
python -B -m unittest discover -s validation/2026-11-08/classic -p test_status_counts.py -v
python -B -m unittest discover -s skills/agent-team-skill/scripts -p test_evidence.py -v
```

这些命令复现数值/函数及证据脚本测试，不会重新派遣集群成员，也不等于重做一轮真实协作验收。

## 记录解释与边界

- `evidence.json` 或独立检查 JSON 保留实际 argv、cwd、退出码、输出和前后源码哈希；日志及快照目录保留原记录。历史 cwd 和辅助脚本路径按当时的本机环境保存，换机器时须调整路径，不能把历史记录当作新执行。
- 工程物理审查可在独立证据目录记录命令。经典 sentry 的原角色禁止写文件，因此它执行只读捕获程序并返回 JSON stdout，由协调者转录保存；这些是本地报告，不是服务端签名或身份认证。
- `validation/**` 通过 `.gitattributes` 禁用文本换行转换，避免 Git 改写冻结副本及日志字节，破坏记录中的 SHA-256。
- 工程物理组覆盖有限正向路径；经典组还实际经历了一次冻结失败、解冻、设计修订和重新验收。没有穷举取消、权限拒绝、任意模型或宿主兼容性、全部故障恢复分支和科研生产任务。
- 冻结和哈希是版本与已观察漂移检查，不是操作系统写锁，也不能排除两次观察之间的短暂修改后恢复。

源码及公开证据的文件哈希见 `manifest.json`。
