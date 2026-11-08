# 本地记录与证据

所有路径属于本轮任务工作区，不在技能安装目录保存任务数据。使用新的 `.agent-team/<run_id>/`，避免与旧轮次共用文件。

协调者维护 `run.json`：本轮用户请求、集群、工作区、逐项已回答的 model/effort、角色真实协作标识、授权文件及负责人、任务依赖和状态、Design ID、Snapshot ID、审查报告路径及未决事项。任务依赖不得有环。每次状态变化追加到 `events.jsonl`，注明观察时间、动作、实际角色标识和依据。重大选择仅以本聊天真实用户答复为准，不让角色代答。

`scope.json` 使用以下字段；workspace 是任务工作区绝对路径，files 是明确授权的相对文件列表，不能是目录：

```json
{
  "workspace": "C:/path/to/project",
  "design_id": "实际计算的设计 SHA-256",
  "files": ["src/main.py", "tests/test_main.py"]
}
```

将下列示例中的 SKILL_DIR 替换为本技能绝对目录，RUN_DIR 替换为本轮记录目录。使用 exec 工具真正执行，不能只写命令就声称执行过：

```text
python -B SKILL_DIR/scripts/evidence.py design RUN_DIR/design.md
python -B SKILL_DIR/scripts/evidence.py run RUN_DIR/scope.json RUN_DIR/evidence -- python -m unittest
python -B SKILL_DIR/scripts/evidence.py snapshot RUN_DIR/scope.json RUN_DIR/snapshots
python -B SKILL_DIR/scripts/evidence.py check RUN_DIR/snapshots/<目录>/snapshot.json
python -B SKILL_DIR/scripts/evidence.py run RUN_DIR/scope.json RUN_DIR/evidence --snapshot RUN_DIR/snapshots/<目录>/snapshot.json -- python -m unittest
```

- design 输出设计文件字节的 SHA-256；设计和设计引用的范围一起审查。设计修改后另存新版本，更新 scope 并重新审查。
- run 直接执行 argv，shell=False，cwd 固定为 workspace；输出唯一的新证据目录，包含 evidence.json、stdout.log、stderr.log。日志保留子进程原始字节。记录命令前后源码哈希、实际退出码和超时；不提供写入沙箱。设计审查可以包含尚不存在的文件，其哈希明确为空。调用 run 的角色必须亲自检查并引用结果，不能把命令成功当作审查通过。
- snapshot 保存实际文件副本、源码哈希、Design ID 和内容关联 Snapshot ID；文件都必须存在。每次生成独立目录，旧快照不覆盖。
- 冻结验证指定 --snapshot，脚本在前后检查源码和快照副本；已观察到的漂移会留下永久 invalid.json，恢复原字节也不能让旧快照重新有效。check 检查同一对象。即使命令退出 0，漂移或超时也使证据无效。
- 解冻由协调者追加事件，注明旧 Snapshot ID、原因及待修复项；旧副本不修改。修复后生成新快照，新快照需要重新独立审查。
- 审查报告关联本轮真实协作身份、Design ID、Snapshot ID、命令证据路径、结论及覆盖边界。工程和物理审查分别保存，审查作者不能与设计/实施作者相同。只读角色原文禁止任何文件写入时，直接用原生 exec 工具执行允许的检查和哈希命令，返回真实 argv、cwd、退出码、stdout/stderr、前后哈希，由协调者保存原始返回。不要声称这些命令由证据脚本捕获或经服务端认证；协调者自己的复测也不能冒充该角色的独立执行。

这些文件提供可审阅的记录，不证明记录作者已经过服务端身份认证。角色、授权、依赖和审查顺序由技能协议核对。执行命令以当前用户权限运行；超时不承诺回收全部子孙进程。
