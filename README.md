# 信息来源权限与采集规则校验模板 | Source Rights Gate

能打开一个网页，不代表可以抓取全文、长期存储、制作摘要或公开展示。这个离线规则模板帮助采集与内容团队把**来源选择、权利复核、运行开关和具体用途**分别记录，在执行某一步前查询是否允许，并看到拒绝原因。

Being able to open a webpage does not establish permission to collect full text, retain it, summarize it, or display it publicly. This offline policy template helps collection and content teams keep **source selection, rights review, operational switches, and intended use** separate, then ask for a reasoned allow/deny decision before a step runs.

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## 从含糊许可到明确决策 / From vague flags to explicit decisions

| 中文 | English |
| --- | --- |
| **区分用途：**对元数据、全文、摘要、公开展示分别判断，也区分内部与公开环境。 | **Separate uses:** evaluate metadata, full text, summaries, and public display independently for internal or public environments. |
| **默认稳妥：**待复核、被拒绝、停用或缺少必要权限的来源不能通过；不一致的清单会在校验时报告。 | **Fail closed:** pending, rejected, disabled, or insufficiently authorized sources are denied; inconsistent registry entries fail validation. |
| **便于流程接入：**本地 JSON 清单配合命令行查询，返回 `allowed` 与 `reasons`，可用返回码阻断批处理或 CI 的下一步。 | **Gate a workflow:** query a local JSON registry for `allowed` and `reasons`, and use exit codes to stop a batch job or CI step. |

适合在采集、摘要或发布流程前设置可检查的配置门。**规则结论依赖你录入的真实权利复核结果**；程序不会替你解读网站条款或授予授权。 / Use it as a configuration gate before collection, summarization, or publication. **Decisions depend on the rights review you enter**; the program does not interpret terms or grant permission.

## Try it / 立即试用

Python 3.9+; no third-party packages. / Python 3.9+，无第三方依赖。

```bash
python3 rights_gate.py examples/sources.json
python3 rights_gate.py examples/sources.json --source fictional-public --environment public --purpose public
python3 -m unittest discover -s tests -v
```

示例查询会返回 `"allowed": true` 和空的 `reasons`；将来源换成 `fictional-internal` 并查询公开用途，可看到拒绝原因。 / The sample query returns `"allowed": true` and an empty `reasons` list. Query `fictional-internal` for public use to see why access is denied.

The `example.*` entries are **fictional policy fixtures**, not verified grants of real-world rights. The program never fetches those URLs. / 样本只是虚构的规则测试数据，不代表真实授权；程序不会访问这些网址。

**License / 许可证：** [Apache-2.0](LICENSE). **Repository / 仓库：** [workstonedai-collab/source-rights-gate](https://github.com/workstonedai-collab/source-rights-gate).
