# IO Contract v0.1

## 输入 CSV

### 文件格式

- CSV；
- 每一行对应一个原始采样点；
- 原始采样率固定为 125 Hz；
- 时间戳单位为秒。

### 必要字段

读取时必须对字段名执行 `strip()` 后匹配。

| 逻辑字段 | 原始字段示例 | 说明 |
|---|---|---|
| time_s | `Time [s]` | 时间戳，单位秒 |
| ecg | ` II` | ECG 单导联，字段名可能有前导空格 |
| ppg | ` PLETH` / `PLETH` | PPG，字段名可能有前导空格 |

### 示例文件

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

## 输出 CSV

### 输出采样率

- 50 Hz。

### 输出行组织

已确认默认假设：

- 主输出 CSV 按 50 Hz 采样点逐行输出；
- 每行包含降采样后的时间戳、ECG、PPG；
- R 峰相关字段只在对应 R 峰行填充；
- 非 R 峰行的 R 峰 / RR 字段为空。

### 输出字段

| 字段 | 类型建议 | 是否必需 | 说明 |
|---|---:|---:|---|
| time_s_50hz | float | 是 | 降采样后的时间戳，单位秒 |
| ecg_50hz | float | 是 | 降采样后的 ECG |
| ppg_50hz | float | 是 | 降采样后的 PPG |
| r_peak_sample_index | int / empty | 是 | R 峰映射到 50 Hz 输出中的采样点索引 |
| r_peak_time_s | float / empty | 是 | R 峰时间，单位秒 |
| rr_ms | float / empty | 是 | 与前一个 R 峰之间的 RR 间期，单位 ms。第一个 R 峰通常为空 |
| detector_name | str / empty | 是 | detector 名称 |
| quality_flag | str / empty | 是 | 质量标志。MVP 可使用 `ok` / `unknown` / `error` |

## 统一 detector 输出

后续 detector adapter 的统一输出至少包括：

| 字段 | 说明 |
|---|---|
| r_peak_sample_index | R 峰在 detector 输入采样率下的样本索引 |
| r_peak_time_s | R 峰时间，单位秒 |
| rr_ms | RR 间期，单位 ms |
| detector_name | detector 名称 |
| detector_version | detector 版本，建议保留在中间结构或日志中 |
| quality_flag | 质量标志，可选 |
| error_message | 错误信息，可选 |

当前主输出 CSV 不强制导出 `detector_version`，但 M2a/M3 应记录 detector 版本，便于追溯。
