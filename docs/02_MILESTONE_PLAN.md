# Milestone Plan v0.1

## M0：项目启动问诊

已完成。

产出：

- 项目启动问诊表；
- 关键事实确认；
- Project Brief v0.1。

## M1：项目启动包

当前里程碑。

目的：

- 建立项目仓库的文档和协作基础；
- 固化 Project Brief、IO Contract、detector 策略、Codex 运行规则；
- 提供最小 Python 项目骨架；
- 将示例 CSV 放入仓库 fixture 路径。

不做：

- 完整算法实现；
- 第三方库集成；
- 完整 GUI；
- 准确率结论。

通过标准：

- 文档齐全；
- 示例 CSV 位于 `tests/fixtures/bidmc_01_Signals_4000.csv`；
- 最小 Python 包结构存在；
- `docs/10_CODEX_NEXT_TASK.md` 指向下一阶段 M2a；
- 无未确认 S0 决策被写入实现。

## M2a：第三方 R 峰检测库评估与选型

目的：

- 评估至少 2-3 个第三方 ECG R 峰 / QRS 检测候选库；
- 使用示例 CSV 做 smoke test；
- 比较 license、安装、维护、桌面端打包风险；
- 判断输出是否可映射到统一 IO Contract；
- 输出 Owner 可决策的推荐方案。

不做：

- 完整 GUI；
- 完整 detector 集成；
- 临床准确性声明；
- 将单个 CSV 结果作为总体准确性结论。

通过标准：

- 至少 2 个候选库完成实际运行或明确记录不可运行原因；
- 输出 `docs/06_THIRD_PARTY_EVAL.md`；
- 给出主方案和无 fallback 策略下的风险；
- 形成 S0 Owner 决策项。

## M2b：数据读取与降采样管线

目的：

- 实现 CSV 读取；
- 支持字段名 `strip()` 归一化；
- 检查采样率约为 125 Hz；
- ECG、PPG、时间戳同步降采样到 50 Hz；
- 输出 M2b 中间结果 CSV。

## M3：Detector Adapter 集成与 RR 输出

目的：

- 根据 M2a Owner 决策，集成选定 detector；
- 通过 adapter 输出统一 R 峰和 RR 结果；
- 不允许 GUI / CLI / 导出模块散落调用第三方库 API。

## M4：CLI 与导出结果完善

目的：

- 完成 CLI 入口；
- 支持输入 CSV 和输出 CSV；
- 导出完整 IO Contract 字段；
- 完成基于 fixture 的 smoke test。

## M5：最小 GUI 与波形可视化

目的：

- 选择 CSV；
- 运行分析；
- 显示 ECG 波形；
- 标记 R 峰；
- 支持导出结果。

## M6：验收、文档收敛与风险复盘

目的：

- 汇总测试；
- 梳理限制；
- 明确后续优化建议；
- 避免将工程工具误表述为医疗诊断软件。
