# AGENTS.md｜Codex / Agent 协作规则

## 项目角色

- Owner：负责目标、约束、关键决策和阶段确认；
- Architect / Reviewer：负责规格整理、任务拆分、源码 / 测试审查、风险归类和里程碑推进建议；
- Runner / Codex：负责按任务文件编码、运行测试和报告结果。

## 必须遵守的规则

1. 先读取：
   - `docs/00_PROJECT_BRIEF.md`
   - `docs/01_DECISION_LOG.md`
   - `docs/02_MILESTONE_PLAN.md`
   - `docs/03_ALGORITHM_SCOPE.md`
   - `docs/04_IO_CONTRACT.md`
   - `docs/05_DETECTOR_STRATEGY.md`
   - `docs/09_CODEX_RUNBOOK.md`
   - `docs/10_CODEX_NEXT_TASK.md`
2. 当前任务以 `docs/10_CODEX_NEXT_TASK.md` 为准。
3. 不得访问 ChatGPT sources、聊天附件或外部不可见文件。
4. 所有测试数据必须使用仓库内相对路径。
5. 示例 CSV 路径固定为：
   ```text
   tests/fixtures/bidmc_01_Signals_4000.csv
   ```
6. 不得擅自改变输入 / 输出字段。
7. 不得擅自改变 detector 策略。
8. 不得把本项目描述为医疗诊断软件。
9. 如果引入第三方依赖，必须写入依赖文件并记录版本。
10. 如果涉及第三方 detector 集成，必须通过 adapter 封装，不得在 GUI / CLI / 业务流程中散落调用第三方库 API。

## 输出摘要要求

Codex 完成任务后，请在回复中至少包含：

1. Summary；
2. Changed files；
3. Test commands；
4. Test results；
5. Known limitations；
6. 未完成事项；
7. 如果涉及第三方库，说明依赖变更、库版本、adapter 或实验脚本位置、运行结果。

## S0 决策项

遇到以下事项必须暂停并报告，不能擅自决定：

- 改变核心算法策略；
- 决定采用某个第三方库作为最终主方案；
- 从第三方库方案切换为完全自研算法；
- 改变是否保留自研 fallback；
- 改变输入 / 输出 API；
- 改变输入 / 输出文件字段；
- 改变技术栈；
- 改变部署平台；
- 改变准确性评价指标；
- 放宽或改变性能、内存、运行时间等工程约束；
- 删除 Owner 已确认需求；
- 将研究 / 工程工具扩展为医疗诊断用途。
