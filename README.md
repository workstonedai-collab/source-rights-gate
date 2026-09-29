# 信息来源权限与采集规则校验模板 | Source Rights Gate

Make every planned source use an explicit decision. This offline template checks a JSON source registry and answers whether a configured source may be used for metadata, full text, summaries, or a public representation in a named environment. Missing permissions fail closed; results explain the denial.

把“可抓取、可存储、可摘要、可公开展示”拆成明确的决定。这个离线模板校验 JSON 来源清单，并对指定环境和用途给出允许或拒绝及原因。缺少授权字段时默认拒绝。

**Read in your language / 选择语言：** [完整中文说明](README.zh-CN.md) · [Full English guide](README.en.md)

## Try it / 立即试用

Python 3.9+; no third-party packages. / Python 3.9+，无第三方依赖。

```bash
python3 rights_gate.py examples/sources.json
python3 rights_gate.py examples/sources.json --source fictional-public --environment public --purpose public
python3 -m unittest discover -s tests -v
```

The `example.*` entries are **fictional policy fixtures**, not verified grants of real-world rights. The program never fetches those URLs. / 样本只是虚构的规则测试数据，不代表真实授权；程序不会访问这些网址。

**License / 许可证：** [Apache-2.0](LICENSE). **Repository / 仓库：** [workstonedai-collab/source-rights-gate](https://github.com/workstonedai-collab/source-rights-gate).
