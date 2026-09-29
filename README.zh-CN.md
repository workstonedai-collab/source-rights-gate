# 信息来源权限与采集规则校验模板

“能打开网页”不等于“能抓全文、长期存储或公开摘要”。这个小工具把来源选择、权利复核、实际运行开关和使用目的分开记录；每次查询都给出明确的允许/拒绝结果及理由。它适合作为采集流程前的一道**可审计配置门**。

[English guide](README.en.md) · [双语首页](README.md)

## 解决什么问题

- 不再用一个含糊的 `allowed=true` 同时代表抓取、存储与公开。
- 待复核、被拒绝或停用的来源，即使出现在清单中也不能被使用。
- “内部可用”和“公开可用”分别判断；公开使用要求更明确的复核状态和展示字段。
- 错误配置在启动前报错，例如重复来源 ID、非 HTTPS 地址、尚未批准却启用。

## 30 秒开始

需要 Python 3.9 或更新版本，无第三方依赖。在本文件夹执行：

```bash
# 校验整个清单
python3 rights_gate.py examples/sources.json

# 查询某个来源能否公开展示标题、链接与摘要
python3 rights_gate.py examples/sources.json \
  --source fictional-public --environment public --purpose public

# 看一条内部来源为什么不能公开
python3 rights_gate.py examples/sources.json \
  --source fictional-internal --environment public --purpose public
```

查询输出示例：

```json
{
  "source_id": "fictional-internal",
  "environment": "public",
  "purpose": "public",
  "allowed": false,
  "reasons": ["environment_not_enabled", "public_review_required"]
}
```

实际结果可能还有其他拒绝理由；机器可直接读取 `allowed` 与 `reasons`。

## 清单结构与规则

参考 [虚构来源清单](examples/sources.json)。每条来源包括：

| 字段 | 作用 |
| --- | --- |
| `id`, `name`, `feed_url` | 标识和 HTTPS 地址；ID 与地址不可重复 |
| `selection` | `accepted`、`pending` 或 `rejected` |
| `rights.review_status` | `pending`、`approved_internal`、`approved_public` 或 `rejected` |
| `rights.fetch_metadata` | 是否允许获取元数据 |
| `rights.fetch_fulltext`, `rights.store_fulltext` | 获取与存储全文分别授权，全文用途必须两者同时为真 |
| `rights.summarize` | 是否允许制作摘要 |
| `rights.public_title_link`, `rights.public_summary` | 公开标题链接与公开摘要分别授权 |
| `operations.enabled`, `operations.environments` | 当前是否启用，以及内部/公开环境范围 |

可查询用途是 `metadata`、`fulltext`、`summary`、`public`；环境是 `internal` 或 `public`。只有来源已接受、权利复核完成、运行开关打开、环境匹配，且该用途的每个权限字段都为真时才允许。`public` 用途同时要求获取元数据、制作摘要、公开标题链接与摘要四项权限，以及 `approved_public` 复核和公开环境。

`review_status` 是**你的组织录入的复核结论**；程序不会自动判断网页条款、版权或合同，也不会根据域名推断授权。样本中 `fictional-*` 条目只是用来演示规则，不能移作真实来源许可记录。

## 用于自己的流程

1. 复制 JSON 样例为自己的本地清单，替换为已经完成来源和权利复核的记录。
2. 先运行不带 `--source` 的完整校验，再逐个查询实际将用到的环境与用途。
3. 只在 `allowed=true` 时继续对应步骤，并把拒绝理由交给负责人处理。
4. 对公开内容另行做事实、敏感信息和编辑审核；本工具只负责配置门。

校验成功返回 `0`；明确拒绝返回 `1`；文件或清单不合法返回 `2`。可以在 CI 或批处理里按返回码阻断后续步骤。

## 隐私与发布边界

程序只读本地 JSON，不抓网页、不向外发请求、不记录凭据。公开样例仅用保留示例域名和虚构复核状态，不包含真实来源名单、运营状态、合同、内部地址或密钥。请勿把实际权利审查材料直接放进公开仓库。

这是独立项目，不继承原业务仓库历史。代码采用 [Apache-2.0 许可证](LICENSE)，公开仓库位于 [workstonedai-collab/source-rights-gate](https://github.com/workstonedai-collab/source-rights-gate)。实际业务使用仍需由你的来源和权利负责人核定。
