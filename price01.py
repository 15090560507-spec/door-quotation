import streamlit as st
import pandas as pd
from datetime import datetime
import json

# --- 1. 页面配置 ---
st.set_page_config(page_title="西州将军门业 - 智能报价系统", layout="wide")

# --- 2. 加载产品库 ---
@st.cache_data
def load_library():
    try:
        return pd.read_csv("library.csv")
    except:
        return pd.DataFrame({"name": ["示例产品1", "示例产品2"], "unit": ["m²", "m²"], "price": [1000, 2000]})

df_lib = load_library()

# --- 3. 侧边栏：基础信息 ---
st.sidebar.header("📋 基础信息")
customer = st.sidebar.text_input("致 (客户)", "张仕玉")
project = st.sidebar.text_input("项目名称", "龙井村322号")
date_str = st.sidebar.date_input("日期", datetime.today()).strftime("%Y.%m.%d")

# --- 4. 主界面：多行产品录入 ---
st.header("🛒 产品明细录入")
st.caption("提示：点击表格下方的 ➕ 可以增加新项；点击行号可删除。")

# 初始化表格数据
if 'items' not in st.session_state:
    st.session_state.items = pd.DataFrame([{
        "品名型号": "0.8的纯铜两定两开门", "长": 2480, "宽": 2690, 
        "开启方向": "内右开", "单位": "m²", "数量": 6.6712, "单价": 6000.0
    }])

# 使用数据编辑器实现“加项”功能
edited_df = st.data_editor(
    st.session_state.items,
    num_rows="dynamic", # 允许动态增加行
    column_config={
        "品名型号": st.column_config.SelectboxColumn("品名型号", options=df_lib['name'].tolist(), required=True),
        "开启方向": st.column_config.SelectboxColumn("开启方向", options=["内右开", "内左开", "外右开", "外左开"]),
        "数量": st.column_config.NumberColumn("数量", format="%.4f"),
        "单价": st.column_config.NumberColumn("单价", format="%.2f"),
    },
    use_container_width=True,
    key="data_editor"
)

# 自动计算逻辑 (金额计算)
edited_df['总金额'] = (edited_df['数量'] * edited_df['单价']).round(0)
grand_total = int(edited_df['总金额'].sum())

# 数字转大写函数
def to_chinese_upper(num):
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整"

total_upper = to_chinese_upper(grand_total)

# --- 5. 1:1 高清 HTML 预览与导出 ---
# 将明细转换为 HTML 表格行
rows_html = ""
for i, row in edited_df.iterrows():
    rows_html += f"""
    <tr>
        <td>{i+1}</td>
        <td style="text-align:left;">{row['品名型号']}</td>
        <td>{row['长']}</td><td>{row['宽']}</td>
        <td>{row['开启方向']}</td><td>{row['单位']}</td>
        <td>{row['数量']}</td><td>{row['单价']}</td>
        <td>{int(row['总金额'])}</td>
    </tr>
    """

# 补全空行
for i in range(len(edited_df), 5):
    rows_html += "<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>"

html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        .no-print {{ text-align: center; margin-bottom: 20px; }}
        .btn {{ padding: 10px 20px; background: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
        #pdf-btn {{ background: #0071e3; margin-left: 10px; }}
        #paper {{ width: 850px; background: white; padding: 40px; margin: auto; font-family: "SimSun", serif; color: black; }}
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; }}
        th, td {{ border: 1.5px solid black; padding: 6px; }}
        .bg-blue {{ background: #00BFFF !important; font-weight: bold; }}
        .bg-yellow {{ background: #FFFF00 !important; color: red; font-weight: bold; text-align: left; padding: 10px; font-size: 12px; border: 1.5px solid black; border-top: none; }}
        @media print {{ .no-print {{ display: none; }} body {{ background: white; }} #paper {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="btn" onclick="exportJPG()">📸 点击下载高清 JPG</button>
        <button class="btn" id="pdf-btn" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
    </div>
    <div id="paper">
        <h2 style="text-align:center; letter-spacing: 2px;">浙江西州将军门业有限公司</h2>
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-weight:bold;">
            <div>致：{customer}<br>项目名称：{project}</div>
            <div style="text-align:right;">日期：{date_str}</div>
        </div>
        <table>
            <tr><th rowspan="2">序号</th><th rowspan="2" width="30%">品名型号</th><th colspan="2">规格</th><th rowspan="2">开启方向</th><th rowspan="2">单位</th><th rowspan="2">数量</th><th rowspan="2">单价</th><th rowspan="2">总金额</th></tr>
            <tr><th>长</th><th>宽</th></tr>
            {rows_html}
            <tr class="bg-blue"><td colspan="8" style="text-align:left;">合计</td><td>{grand_total}</td></tr>
        </table>
        <div style="border:1.5px solid black; border-top:none; padding:8px; font-weight:bold;">
            合计总金额 (大写): <span style="margin-left:20px;">{total_upper}</span>
        </div>
        <div class="bg-yellow">
            1. 付款方式: 确定制作，先安排货款50%的定金，款清发货<br>
            2. 以上价格不包含运费、安装调试费、测量等费用。<br>
            汇款账号：张春兰 622848 0329 2739 08775 (农业银行)
        </div>
    </div>
    <script>
        function exportJPG() {{
            const target = document.getElementById('paper');
            html2canvas(target, {{ scale: 2 }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '报价单_{customer}.jpg';
                link.href = canvas.toDataURL('image/jpeg', 0.9);
                link.click();
            }});
        }}
    </script>
</body>
</html>
"""

# 在预览区渲染
st.components.v1.html(html_template, height=1000, scrolling=True)
