# Codex Runbook v0.1

## 默认执行指令

Owner 给 Codex 的默认指令：

```text
请读取 docs/10_CODEX_NEXT_TASK.md，并严格执行。
```

## 环境建议

建议使用 Python 3.10+。

初始化环境示例：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

如果当前任务允许安装第三方库，必须：

1. 将依赖写入 `requirements.txt` 或 `pyproject.toml`；
2. 在任务输出中记录实际版本；
3. 说明安装是否成功；
4. 如果安装失败，说明错误原因和替代建议。

## 当前 fixture

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

CSV 关键字段：

- `Time [s]`
- ` II`
- ` PLETH`

读取时应对字段名执行 `strip()` 后匹配。

## M1 最小测试命令

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
```

M1 不要求完整算法运行。

## 后续算法类任务的测试要求

如果任务涉及算法处理、CLI、GUI、第三方库集成或导出功能，且仓库中已有示例 CSV，则验收标准必须包含基于该示例 CSV 的测试。

测试命令必须使用仓库内相对路径，例如：

```bash
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/result.csv
```

不得使用：

- “使用 sources 中的 CSV 文件”；
- “使用用户上传的 CSV 文件”；
- “使用聊天附件中的 CSV 文件”。
