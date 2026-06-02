---
name: 二级：Excel处理
---

# 二级：Excel处理（XLSX）

**适用场景**：用户需要创建/分析/编辑Excel表格、公式计算、数据可视化

---

## 工具对比

| 工具 | 公式计算 | 图表 | 大文件 | 推荐场景 |
|------|---------|------|--------|------------|
| **openpyxl** | ✅ | ✅ | 中（10万行） | 读写XLSX（推荐） |
| **pandas** | 通过公式 | ✅（matplotlib） | 大（100万行） | 数据分析/清洗 |
| **xlsxwriter** | ✅ | ✅ | 大 | 只写不读，高性能 |
| **xlwings** | ✅（调用Excel） | ✅ | 中 | 需要Excel交互 |

---

## 三级执行：openpyxl（推荐，读写XLSX）

**触发词**：创建Excel、编辑表格、Excel加公式、生成XLSX

### 安装

```bash
pip install openpyxl
```

### 创建新Excel

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

# 创建Workbook
wb = Workbook()
ws = wb.active
ws.title = "数据表"

# 写入标题行（加粗+背景色）
headers = ["姓名", "年龄", "城市", "薪资"]
for col, header in enumerate(headers, start=1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
    cell.alignment = Alignment(horizontal="center")

# 写入数据
data = [
    ["张三", 25, "北京", 10000],
    ["李四", 30, "上海", 15000],
    ["王五", 28, "广州", 12000],
]
for row_idx, row_data in enumerate(data, start=2):
    for col_idx, value in enumerate(row_data, start=1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# 添加公式
ws.cell(row=2, column=5, value "=D2*1.1")  # 加薪10%
ws.cell(row=3, column=5, value "=D3*1.1")
ws.cell(row=4, column=5, value "=D4*1.1")

# 调整列宽
for col in range(1, ws.max_column + 1):
    ws.column_dimensions[get_column_letter(col)].width = 15

# 保存
wb.save("output.xlsx")
```

### 读取Excel

```python
from openpyxl import load_workbook

# 打开现有Excel
wb = load_workbook("input.xlsx")
ws = wb.active

# 读取所有数据
for row in ws.iter_rows(values_only=True):
    print(row)

# 读取指定单元格
print(ws["A1"].value)
print(ws.cell(row=1, column=1).value)

# 获取最大行/列
print(f"最大行：{ws.max_row}")
print(f"最大列：{ws.max_column}")
```

### 编辑现有Excel

```python
from openpyxl import load_workbook

wb = load_workbook("input.xlsx")
ws = wb.active

# 修改单元格
ws["A1"] = "新标题"

# 插入行
ws.insert_rows(2)

# 删除列
ws.delete_cols(3)

# 添加筛选
ws.auto_filter.ref = f"A1:D{ws.max_row}"

# 冻结首行
ws.freeze_panes = "A2"

# 保存修改
wb.save("modified.xlsx")
```

### 添加图表

```python
from openpyxl.chart import BarChart, Reference

# 创建柱状图
chart = BarChart()
chart.title = "薪资对比"
chart.x_axis.title = "姓名"
chart.y_axis.title = "薪资"

# 选择数据范围
data = Reference(ws, min_col=4, min_row=1, max_row=4)
cats = Reference(ws, min_col=1, min_row=2, max_row=4)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# 插入图表
ws.add_chart(chart, "G2")

wb.save("chart.xlsx")
```

---

## 三级执行：pandas（数据分析/清洗）

**触发词**：分析Excel数据、统计、清洗数据、数据透视表

### 安装

```bash
pip install pandas openpyxl
```

### 使用

```python
import pandas as pd

# 读取Excel
df = pd.read_excel("input.xlsx")
print(df.head())

# 基本统计
print(df.describe())
print(df.mean())
print(df.groupby("城市")["薪资"].mean())

# 筛选数据
high_salary = df[df["薪资"] > 12000]
print(high_salary)

# 添加列
df["加薪后"] = df["薪资"] * 1.1

# 数据透视表
pivot = pd.pivot_table(df, values="薪资", index="城市", aggfunc="mean")
print(pivot)

# 保存到Excel
df.to_excel("output.xlsx", index=False)

# 多个Sheet
with pd.ExcelWriter("output.xlsx") as writer:
    df.to_excel(writer, sheet_name="Sheet1", index=False)
    pivot.to_excel(writer, sheet_name="透视表")
```

---

## 三级执行：xlsxwriter（只写不读，高性能）

**触发词**：生成大型Excel、高性能写入

### 安装

```bash
pip install xlsxwriter
```

### 使用

```python
import xlsxwriter

# 创建Workbook
workbook = xlsxwriter.Workbook("output.xlsx")
worksheet = workbook.add_worksheet()

# 写入数据
worksheet.write("A1", "姓名")
worksheet.write("B1", "年龄")
worksheet.write(1, 0, "张三")  # 行1，列0
worksheet.write(1, 1, 25)

# 添加图表
chart = workbook.add_chart({"type": "column"})
chart.add_series({"values": "=Sheet1!$D2:$D4"})
worksheet.insert_chart("G2", chart)

workbook.close()
```

---

## 使用建议

1. **读写XLSX（推荐）** → openpyxl
2. **数据分析/清洗** → pandas
3. **只写不读，高性能** → xlsxwriter
4. **需要Excel交互（格式/宏）** → xlwings（需要安装Excel）
5. **大文件（100万行+）** → pandas（分块读取）
