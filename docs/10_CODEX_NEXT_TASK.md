# M2a Codex Task｜第三方 R 峰检测库评估与选型

## 0. 执行前必须阅读

请先阅读以下文档：

- `docs/00_PROJECT_BRIEF.md`
- `docs/01_DECISION_LOG.md`
- `docs/02_MILESTONE_PLAN.md`
- `docs/03_ALGORITHM_SCOPE.md`
- `docs/04_IO_CONTRACT.md`
- `docs/05_DETECTOR_STRATEGY.md`
- `docs/09_CODEX_RUNBOOK.md`
- `AGENTS.md`

## 1. 当前里程碑

M2a：第三方 R 峰检测库评估与选型。

## 2. 本轮目标

评估第三方 ECG R 峰 / QRS 检测候选库，判断其是否适合本项目，并基于示例 CSV 做 smoke test。

至少评估 2-3 个候选库，优先考虑：

1. NeuroKit2；
2. WFDB；
3. BioSPPy；
4. SleepECG；
5. HeartPy；
6. scipy / numpy signal processing 组合方案。

不要求所有候选库都能运行成功，但必须记录：

- 成功运行的库；
- 无法安装或无法运行的库；
- 无法运行的原因；
- 是否仍值得后续考虑。

## 3. 本轮非目标

本轮不做：

1. 完整 GUI；
2. 完整 CLI 分析流程；
3. 正式 detector adapter 集成；
4. 完整算法优化；
5. 医疗诊断结论；
6. 临床级准确性声明；
7. 把单个 CSV 的结果作为总体准确性结论；
8. 锁死不可替换的库接口。

## 4. 允许修改范围

允许新增或修改：

- `docs/06_THIRD_PARTY_EVAL.md`；
- `tools/` 下的 M2a 临时评估脚本；
- `requirements.txt`；
- `pyproject.toml` 中与 M2a 评估必要相关的依赖；
- 最小测试文件，例如 `tests/test_m2a_eval_smoke.py`；
- 如确有必要，可补充 `docs/05_DETECTOR_STRATEGY.md` 的“评估记录引用”，但不得改变已确认策略。

## 5. 不允许修改范围

未经 Owner 决策，不得修改：

1. `docs/04_IO_CONTRACT.md` 中已确认的输入 / 输出字段；
2. 是否保留自研 fallback；
3. R 峰检测时机：当前已确认优先在 125 Hz 原始 ECG 上检测，再映射到 50 Hz 输出；
4. 项目用途边界；
5. 技术栈；
6. 示例 CSV 路径；
7. 将某个第三方库写成最终主方案。

## 6. 示例 CSV

必须使用仓库内相对路径：

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

关键字段：

- 时间戳：`Time [s]`
- ECG：` II`，注意字段名前有空格，读取时必须 `strip()` 匹配为 `II`
- PPG：` PLETH`，读取时必须 `strip()` 匹配为 `PLETH`

## 7. Smoke test 要求

对每个可运行候选库，至少尝试完成：

1. 读取示例 CSV；
2. 使用 `Time [s]` 估计采样率，确认约为 125 Hz；
3. 提取 `II` ECG 序列；
4. 运行 R 峰 / QRS 检测；
5. 输出候选库检测到的 R 峰数量；
6. 输出前若干个 R 峰时间；
7. 计算 RR ms；
8. 检查 RR 是否在基本合理范围，例如 300-2000 ms；
9. 记录 detector 名称和版本；
10. 记录是否能映射到统一 IO Contract。

注意：单个示例 CSV 只作为 smoke test，不作为总体准确性证明。

## 8. 第三方库调用规则

本轮是“评估 / 选型”里程碑。

允许在 `tools/` 下的临时评估脚本中直接调用候选第三方库 API。

不允许在以下位置直接散落调用第三方库 API：

- GUI；
- CLI；
- 导出模块；
- 未来正式业务流程。

后续正式集成必须通过 detector adapter。

## 9. 输出文档要求

必须新增：

```text
docs/06_THIRD_PARTY_EVAL.md
```

该文档至少包含：

1. 候选库列表；
2. 每个库是否支持 R 峰 / QRS 检测；
3. 是否支持 125 Hz 输入，或是否容易适配；
4. 是否容易适配当前 CSV；
5. 输出是否能转换为：
   - `r_peak_sample_index`
   - `r_peak_time_s`
   - `rr_ms`
   - `detector_name`
   - `quality_flag`
6. 是否支持或可处理噪声、漏搏、早搏、信号中断等异常场景，至少记录能力与限制；
7. license 信息；
8. pip / conda 安装情况；
9. 桌面端打包风险；
10. 维护风险；
11. 在示例 CSV 上的 smoke test 结果；
12. 推荐主方案；
13. 不保留自研 fallback 的风险；
14. 需要 Owner 决策的 S0 项。

## 10. 建议测试命令

可根据实际脚本名调整，但必须给出真实执行命令。

示例：

```bash
python -m pytest
python tools/evaluate_detectors.py tests/fixtures/bidmc_01_Signals_4000.csv
```

如果部分库安装失败，测试脚本应能报告失败原因，而不是让整个评估不可读。

## 11. 通过标准

本轮通过需要满足：

1. 至少 2 个候选方案完成实际 smoke test，或明确说明为什么无法完成；
2. `docs/06_THIRD_PARTY_EVAL.md` 完整记录评估结果；
3. 示例 CSV 使用仓库相对路径；
4. 记录候选库版本；
5. 记录 license 和安装方式；
6. 记录 R 峰数量、RR 合理性、输出字段映射可行性；
7. 给出推荐主方案，但不得擅自把推荐方案写成已最终采用；
8. 明确列出 Owner 需要决策的 S0 项；
9. 不改变已确认 IO Contract；
10. 不实现完整 GUI 或正式 detector 集成。

## 12. 失败时应报告的信息

如果无法完成，请报告：

1. 失败的库；
2. 失败原因；
3. 安装日志或关键错误信息；
4. 是否因为环境、依赖、网络、版本、API 不兼容；
5. 是否建议换库或推迟该库；
6. 哪些通过标准未满足。

## 13. Codex 输出摘要要求

完成后请输出：

1. Summary；
2. Changed files；
3. Test commands；
4. Test results；
5. Candidate detector versions；
6. Smoke test result summary；
7. Known limitations；
8. Owner decision needed；
9. 未完成事项。
