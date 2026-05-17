# Third-party R-peak Detector Evaluation v0.1

## 1. 范围与边界

本文件记录 M2a 第三方 ECG R 峰 / QRS 检测库评估结果。

本轮只做评估与选型建议，不做正式 detector adapter 集成，不修改 GUI / CLI / 导出流程，不改变 `docs/04_IO_CONTRACT.md` 中已确认的输入 / 输出字段。

示例 CSV 仅用于 smoke test：

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

读取规则：

- 对 CSV 字段名执行 `strip()`；
- 时间戳字段：`Time [s]`；
- ECG 字段：`II`，原始 CSV 中可为 ` II`；
- PPG 字段：`PLETH`，本轮 detector smoke test 不使用 PPG；
- 使用 `Time [s]` 估计采样率，结果为 125.000000 Hz。

## 2. 评估脚本与安装

临时评估脚本：

```text
tools/evaluate_detectors.py
```

该脚本位于 `tools/`，允许在 M2a 中直接调用第三方库 API。后续 M3 正式集成时，必须通过 `ecg_rr_tool/detectors/` adapter 封装，不得在 GUI / CLI / 导出模块中散落调用第三方库 API。

本轮安装命令使用隔离目录：

```bash
/Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install --target /private/tmp/ecg_m2a_deps neurokit2 wfdb biosppy heartpy sleepecg pytest
/Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install --target /private/tmp/ecg_m2a_deps peakutils
```

`requirements.txt` 已记录 M2a 评估直接依赖：

| 包 | 版本 | 用途 |
|---|---:|---|
| NeuroKit2 | 0.2.13 | 候选 detector |
| WFDB | 4.3.1 | 候选 detector |
| BioSPPy | 2.2.4 | 候选 detector |
| PeakUtils | 1.3.5 | BioSPPy 运行所需间接依赖，本轮需显式安装 |
| HeartPy | 1.2.7 | 候选 detector |
| SleepECG | 0.5.9 | 候选 detector |
| SciPy | 1.17.1 | scipy / numpy 组合候选 |

测试环境中还安装了 `pytest==9.0.3`。`pyproject.toml` 已有 `dev = ["pytest>=7"]`，本轮未改动正式项目依赖入口。

## 3. 候选库结论表

| 候选方案 | R 峰 / QRS 支持 | 125 Hz 适配 | 当前 CSV 适配 | 输出映射 | License | 安装情况 | 桌面端打包风险 | 维护风险 | 本轮结论 |
|---|---|---|---|---|---|---|---|---|---|
| NeuroKit2 `ecg_peaks` | 支持 ECG R 峰检测 | 支持传入 `sampling_rate=125` | 容易，传入 ECG 数组 | 可映射 | MIT | 成功 | 中等偏高，依赖 matplotlib / scikit-learn / scipy 等 | 低到中 | 可作为强候选，但依赖较重 |
| WFDB `processing.xqrs_detect` | 支持 QRS / R 峰检测 | 支持 `fs=125` | 容易，传入 ECG 数组 | 可映射 | MIT | 成功 | 中等，依赖 scipy / pandas / aiohttp / soundfile 等 | 低到中 | 推荐作为 M2a 主方案候选 |
| BioSPPy `signals.ecg.ecg` | 支持 ECG R 峰检测 | 支持 `sampling_rate=125` | 容易，传入 ECG 数组 | 可映射 | BSD 3-clause | 初次安装缺 `peakutils`，补装后成功 | 高，依赖 OpenCV / h5py / matplotlib 等 | 中 | 可运行，但依赖和打包成本偏高 |
| HeartPy `process` | 支持峰检测和心率分析 | 支持 `sample_rate=125` | 容易，传入 ECG 数组 | 可映射 | metadata 为 UNKNOWN，classifier 为 GPL | 成功 | 中等，依赖 scipy / matplotlib | 中 | 本 fixture 有 1 个 RR 越界，不建议作为主方案 |
| SleepECG `detect_heartbeats` | 支持 heartbeat / R 峰检测 | 支持 `fs=125` | 容易，传入 ECG 数组 | 可映射 | BSD 3-clause | 成功 | 中等，含平台 wheel / C 后端，整体较轻 | 中 | 推荐作为备选主方案候选 |
| SciPy bandpass + `find_peaks` | 不是专用 ECG detector，需要项目自定义启发式 | 可适配 | 容易 | 可映射 | BSD 类许可 | 成功 | 低到中 | 低 | 仅作 smoke 对照，不建议作为最终主方案 |

输出字段映射可行性：

| IO Contract 字段 | 映射方式 |
|---|---|
| `r_peak_sample_index` | detector 返回的原始 125 Hz 样本索引 |
| `r_peak_time_s` | 用 `Time [s]` 数组按样本索引查表 |
| `rr_ms` | 相邻 `r_peak_time_s` 差值乘以 1000 |
| `detector_name` | adapter 固定名称，例如 `wfdb_xqrs` |
| `quality_flag` | 本轮 smoke test 使用 `ok` / `unknown` / `error` |

## 4. Smoke Test 结果

执行命令：

```bash
PYTHONPATH=/private/tmp/ecg_m2a_deps MPLCONFIGDIR=/private/tmp/ecg_m2a_mpl /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/evaluate_detectors.py tests/fixtures/bidmc_01_Signals_4000.csv
```

输入：

| 项 | 值 |
|---|---:|
| samples | 4000 |
| estimated_fs_hz | 125.000000 |
| duration_s | 31.992 |

结果：

| 候选方案 | 状态 | 版本 | R 峰数量 | RR ms min / median / max | RR 300-2000 ms 越界数 | 前 8 个 R 峰时间 s |
|---|---|---:|---:|---|---:|---|
| NeuroKit2 `ecg_peaks(method='neurokit')` | success | 0.2.13 | 50 | 624.0 / 640.0 / 648.0 | 0 | 0.400, 1.032, 1.672, 2.320, 2.960, 3.592, 4.240, 4.880 |
| WFDB `processing.xqrs_detect` | success | 4.3.1 | 50 | 624.0 / 640.0 / 656.0 | 0 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 |
| BioSPPy `ecg.ecg` | success | 2.2.4 | 49 | 624.0 / 640.0 / 648.0 | 0 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 |
| HeartPy `process` | success | 1.2.7 | 49 | 224.0 / 640.0 / 1928.0 | 1 | 0.392, 1.032, 1.672, 2.320, 2.960, 3.592, 4.240, 4.880 |
| SleepECG `detect_heartbeats` | success | 0.5.9 | 50 | 624.0 / 640.0 / 656.0 | 0 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 |
| SciPy bandpass + `find_peaks` smoke heuristic | success | 1.17.1 | 50 | 624.0 / 640.0 / 656.0 | 0 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 |

解释：

- NeuroKit2、WFDB、SleepECG、SciPy 对照方案在该 fixture 上均检测到 50 个 R 峰，RR 范围全部落在 300-2000 ms。
- BioSPPy 检测到 49 个 R 峰，已检测 RR 均在基本合理范围；需后续人工查看是否漏掉边界峰。
- HeartPy 检测到 49 个峰，但出现 1 个 224 ms RR，低于本轮基本合理范围；本轮不建议作为主方案。
- SciPy 组合方案只说明该 fixture 上简单启发式可跑通，不等于可作为最终 detector。若采用它作为主方案，会把算法责任转向项目自研调参，和当前“不默认自研 detector”的策略不一致。

## 5. 异常场景能力与限制

| 候选方案 | 噪声 | 漏搏 / 早搏 | 信号中断 | 本轮限制 |
|---|---|---|---|---|
| NeuroKit2 | 有 ECG 清洗与多种峰检测方法，具备一定抗噪能力 | 可输出峰位，但异常解释需项目另行处理 | 需 adapter 捕获异常和空结果 | 本轮只测单个短 fixture，未做噪声注入 |
| WFDB | XQRS 面向 ECG QRS 检测，工程上较贴近需求 | 可返回峰位，异常 beat 识别仍需项目质量层处理 | 需 adapter 处理 detector 失败和空结果 | 本轮未对极端噪声和断点做压力测试 |
| BioSPPy | 包含 ECG filtering / segment 流程 | 可输出峰位和心率序列 | 依赖链较重，失败面较多 | 本轮只验证能运行，未确认漏掉的 1 个峰来源 |
| HeartPy | 偏心率分析工具，峰检测可用 | 本轮出现 224 ms RR 越界 | 需额外清洗和异常策略 | 对 ECG 主检测适配性弱于 ECG 专用工具 |
| SleepECG | 具备 heartbeat detection API | 返回峰位，异常解释需另做 | C 后端 / wheel 可用性需关注 | 包定位偏 sleep ECG，不是通用 ECG 工具箱 |
| SciPy 组合 | 完全取决于项目自定义滤波与阈值 | 需项目自研质量与调参 | 需项目自研异常处理 | 不应在 M2a 后绕过第三方 detector 策略 |

## 6. 推荐方案

M2a 推荐 Owner 决策优先考虑：

1. 主方案候选：WFDB `processing.xqrs_detect`。
2. 备选主方案候选：SleepECG `detect_heartbeats`。
3. 对照候选：NeuroKit2 `ecg_peaks`，若 Owner 更看重多算法工具箱和后续信号处理扩展，可继续考虑。

推荐 WFDB 的原因：

- ECG / PhysioNet 场景契合度高；
- QRS detector API 直接返回样本索引，容易映射到当前 IO Contract；
- MIT license；
- fixture smoke test 结果与 SleepECG / SciPy 对照一致，RR 基本合理；
- 相比 NeuroKit2，少一些面向可视化和机器学习工具箱的额外概念；相比 BioSPPy，避免 OpenCV 这类较重依赖；相比 HeartPy，更贴近 ECG QRS 检测。

这不是最终采用决策。M3 只有在 Owner 明确确认后，才能实现对应 adapter。

## 7. 不保留自研 fallback 的风险

Owner 已确认不保留自研 fallback。本轮识别到的风险：

- 如果最终第三方 detector 安装失败、平台 wheel 缺失或运行时报错，分析流程应 fail fast 并输出明确错误，而不是自动切换到自研峰检测。
- 未来桌面端打包时，依赖链越重，安装包体积和平台兼容风险越高。
- 单个 fixture 不能证明 detector 总体准确性；M3/M4 至少应保留 smoke test 和人工抽查记录。
- 如果最终选择的 detector 对特定噪声、断点或异常节律表现差，项目需要通过质量标志和错误报告管理风险，而不是擅自加入自研 fallback。

## 8. Owner 需要决策的 S0 项

M2a 后进入 M3 前，请 Owner 明确确认：

1. 是否采用 WFDB `processing.xqrs_detect` 作为正式主 detector。
2. 如果不采用 WFDB，是否选择 SleepECG 或 NeuroKit2 作为正式主 detector。
3. 是否接受“不保留自研 fallback”带来的 fail-fast 行为。
4. 是否接受所选 detector 的依赖链与桌面端打包风险。
5. M3 adapter 的 `detector_name` 固定命名，例如 `wfdb_xqrs`。

## 9. 后续建议

- M3 只实现 Owner 确认的一个正式 adapter。
- Adapter 返回统一结构，不改变主输出 CSV 字段。
- CLI / GUI / 导出模块只依赖 factory 或 adapter 接口。
- 保留 `tools/evaluate_detectors.py` 作为 M2a 记录，不进入正式业务路径。
