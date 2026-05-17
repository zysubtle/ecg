# Detector Strategy v0.1

## 已确认策略

- 允许使用第三方 ECG R 峰 / QRS 检测库；
- 允许 Codex 安装 pip 依赖；
- 无 license 限制；
- 不要求商业闭源使用；
- 不保留自研 fallback；
- 算法实现前必须先做 M2a 第三方库评估与选型；
- M2a 结果必须形成 Owner 可决策的 S0 方案。

## 候选库

M2a 至少评估 2-3 个候选库，包括但不限于：

- NeuroKit2；
- WFDB；
- BioSPPy；
- SleepECG；
- HeartPy；
- scipy / numpy signal processing 组合方案。

## Adapter 封装规则

如果采用第三方 R 峰检测库，必须通过 adapter 层封装。

推荐结构：

```text
ecg_rr_tool/detectors/base.py
ecg_rr_tool/detectors/neurokit_detector.py
ecg_rr_tool/detectors/wfdb_detector.py
ecg_rr_tool/detectors/biosppy_detector.py
ecg_rr_tool/detectors/heartpy_detector.py
ecg_rr_tool/detectors/factory.py
```

当前 M1 仅创建最小接口骨架，不集成具体第三方库。

## 不允许事项

未经 Owner 决策，不得：

- 从第三方库方案切换为完全自研算法；
- 从自研算法切换为第三方库方案；
- 改变是否保留 fallback；
- 改变输入 / 输出字段；
- 改变核心算法策略；
- 将工程工具扩展为医疗诊断用途。

## M2a 应评估内容

1. 是否支持 R 峰 / QRS 检测；
2. 是否支持 125 Hz ECG 输入，或是否容易适配；
3. 是否支持当前 CSV 数据格式，或是否容易适配；
4. 输出是否能转换为统一 IO Contract；
5. 是否能处理噪声、漏搏、早搏、信号中断等异常场景，至少记录能力与限制；
6. license 是否明确；
7. 是否适合本项目当前研究 / 工程用途；
8. 是否易于通过 pip / conda 安装；
9. 是否便于打包到桌面端应用；
10. 是否存在维护风险；
11. 是否能在示例 CSV 上通过 smoke test；
12. 在“不保留自研 fallback”前提下的风险。

## M2a 评估记录引用

第三方 detector 评估结果记录在：

```text
docs/06_THIRD_PARTY_EVAL.md
```

该记录仅提供 M2a 推荐方案，最终 detector 选择仍需 Owner S0 决策确认。
