# 五列 KPI 表格模板

当用户提供类似研发绩效考核截图时，默认按以下五列组织：

| 考核维度 | 权重 | 考核项目及目标值 | 衡量标准/关键举措 | 完成情况 |
|---|---:|---|---|---|

## XML 骨架

```xml
<table>
  <colgroup>
    <col width="120"/><col width="90"/><col width="130"/>
    <col width="400"/><col width="360"/>
  </colgroup>
  <thead>
    <tr>
      <th background-color="light-gray">考核维度</th>
      <th background-color="light-gray">权重</th>
      <th background-color="light-gray">考核项目及目标值</th>
      <th background-color="light-gray">衡量标准/关键举措</th>
      <th background-color="light-gray">完成情况</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3">效率提升</td>
      <td rowspan="3">50%</td>
      <td>研发效率</td>
      <td><p>沿用用户提供的考核标准。</p></td>
      <td>
        <p><b>多线交付。</b> 概括完成的业务方向与端到端闭环。</p>
        <p><b>快速响应。</b> 概括对变更、验收和异常的处理。</p>
        <p><b>复用沉淀。</b> 概括可复用模块、流程或方法。</p>
      </td>
    </tr>
  </tbody>
</table>
```

## 完成情况写法

每个单元格先写事实，再写价值。推荐两至三个短段：

- **工作主题。** 说明完成的业务能力、系统范围和关键场景。
- **解决的问题。** 说明处理的风险、异常、协同难点或端间差异。
- **沉淀/价值。** 说明复用能力、体验改善或后续效率收益。

避免只写“已完成”“无问题”“全部达标”，或把提交次数、代码行数、仓库数量写成主要内容。没有外部证据时，不写“零故障”“无投诉”“AI 提效达到 X%”等结论。格式调整不得删除用户已确认的完成情况。
