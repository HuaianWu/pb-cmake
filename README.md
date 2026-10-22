# pb-cmark：从零重写 `cmark`（CommonMark 参考实现）

**难度：hard**　语言：C　上游：[commonmark/cmark](https://github.com/commonmark/cmark) @ `eec0eeb`（0.31.2）

agent 拿到一个只能执行的 `cmark` 二进制文件，以及它的 README 和 man page（不给 CommonMark spec）。它要实现一个完整的 Markdown 解析器和 5 种渲染器：html、xml、man、latex、commonmark。所有开关也要支持：`--sourcepos --hardbreaks --nobreaks --smart --safe/--unsafe --validate-utf8 --width`。

## 测试组成（共 2758 个）

| 来源 | 数量 | 内容 |
|---|---|---|
| harvested | 1391 | spec 示例（全部有 html 版本，同时轮换其他渲染器）、smart punct、regression、实体，以及 25 个缩小版的病态输入（测线性时间） |
| probe | 873 | CLI 开关、13 个示例文档 × 5 种渲染器 × 开关组合、`--width` 换行、字节级边界输入（NUL、CR、BOM、非法 UTF-8） |
| fuzz | 494 | 随机组合 Markdown 片段（种子 31337） |
