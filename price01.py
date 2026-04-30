import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(page_title="西州将军门业 - 智能报价系统", layout="wide")

# ==========================================
# 2. 读取/生成产品库
# ==========================================
@st.cache_data
def load_library():
    if os.path.exists("library.csv"):
        return pd.read_csv("library.csv")
    else:
        # 如果没有文件，生成默认测试库
        return pd.DataFrame({
            "name": ["0.8的纯铜两定两开门", "0.8的不锈钢镀铜:正面1.2mm镀铜蚀刻", "暗合页（子母）", "门柱花件另加"],
            "unit": ["m²", "m²", "套", "m²"],
            "price": [6000, 1680, 1000, 2750]
        })

df_lib = load_library()
product_names = df_lib['name'].tolist()

# ==========================================
# 3. 侧边栏：基础表头信息录入
# ==========================================
with st.sidebar:
    st.header("📝 基础表头录入")
    customer = st.text_input("致 (客户名称)", "张仕玉")
    project = st.text_input("项目名称", "龙井村322号")
    date_str = st.date_input("日期", datetime.today()).strftime("%Y.%m.%d")
    fax = st.text_input("传真", "")
    subject = st.text_input("主题", "")
    st.info("提示：在此处修改客户信息，右侧报价单会自动更新。")

# ==========================================
# 4. 核心工作区：产品明细动态录入 (支持无限加项)
# ==========================================
st.title("🛒 产品明细与报价单预览")
st.caption("👇 在下方表格录入产品。点击表格底部的 **➕ 号** 可增加产品行；选中左侧序号按 **Delete 键** 可删除行。")

# 初始化 Session State 以保存表格数据
if 'quote_items' not in st.session_state:
    st.session_state.quote_items = pd.DataFrame([{
        "品名型号": "0.8的纯铜两定两开门", "长_mm": 2480, "宽_mm": 2690, 
        "开启方向": "外右开", "单位": "m²", "数量": 6.6712, "单价": 6000.0
    }])

# 使用 st.data_editor 实现高自由度编辑
edited_df = st.data_editor(
    st.session_state.quote_items,
    num_rows="dynamic", # 关键：允许动态加项
    column_config={
        "品名型号": st.column_config.SelectboxColumn("品名型号", options=product_names, required=True, width="large"),
        "开启方向": st.column_config.SelectboxColumn("开启方向", options=["内右开", "内左开", "外右开", "外左开", ""]),
        "长_mm": st.column_config.NumberColumn("长(mm)", format="%d"),
        "宽_mm": st.column_config.NumberColumn("宽(mm)", format="%d"),
        "数量": st.column_config.NumberColumn("数量", format="%.4f"),
        "单价": st.column_config.NumberColumn("单价", format="%.2f"),
    },
    use_container_width=True
)

# 联动逻辑：如果用户选了产品，自动在后台匹配单位和单价 (如果用户没填的话)
for idx, row in edited_df.iterrows():
    if pd.notna(row['品名型号']) and row['品名型号'] in product_names:
        matched = df_lib[df_lib['name'] == row['品名型号']].iloc[0]
        # 如果单位为空，自动填入
        if pd.isna(row['单位']) or row['单位'] == "":
            edited_df.at[idx, '单位'] = matched['unit']
        # 强制更新单价（可根据需要决定是否覆盖用户手填的单价）
        # edited_df.at[idx, '单价'] = matched['price']

# 自动计算每行总价与合计总金额
edited_df['总金额'] = (edited_df['数量'] * edited_df['单价']).round(0).fillna(0).astype(int)
grand_total = int(edited_df['总金额'].sum())

# 数字转大写函数
def to_chinese_upper(num):
    if num == 0: return "零元整"
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整"

total_upper = to_chinese_upper(grand_total)

# ==========================================
# 5. 生成 1:1 像素级排版与导出引擎
# ==========================================
st.divider()

# 动态生成表格的 HTML 行
rows_html = ""
for i, row in edited_df.iterrows():
    p_name = row['品名型号'] if pd.notna(row['品名型号']) else ""
    length = row['长_mm'] if pd.notna(row['长_mm']) else ""
    width = row['宽_mm'] if pd.notna(row['宽_mm']) else ""
    direction = row['开启方向'] if pd.notna(row['开启方向']) else ""
    unit = row['单位'] if pd.notna(row['单位']) else ""
    qty = f"{row['数量']:.4f}" if pd.notna(row['数量']) else ""
    price = f"{row['单价']:.0f}" if pd.notna(row['单价']) else ""
    total = row['总金额']

    rows_html += f"""
    <tr>
        <td>{i+1}</td>
        <td style="text-align: left; padding-left: 5px; font-weight: bold;">{p_name}</td>
        <td>{length}</td>
        <td>{width}</td>
        <td>{direction}</td>
        <td>{unit}</td>
        <td>{qty}</td>
        <td>{price}</td>
        <td style="font-weight: bold;">{total}</td>
    </tr>
    """

# 补齐空白行（让表格看起来丰满，像原版 Excel）
empty_rows_needed = max(0, 4 - len(edited_df))
for i in range(empty_rows_needed):
    rows_html += "<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>0</td></tr>"

# 完整的 HTML 模板 (完美对齐您的截图)
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        body {{ font-family: "SimSun", "STSong", serif; background-color: #f0f2f6; margin: 0; padding: 20px; }}
        
        /* 隐藏滚动条 */
        ::-webkit-scrollbar {{ display: none; }}
        
        /* 导出按钮样式 */
        .toolbar {{ text-align: center; margin-bottom: 20px; }}
        .btn {{ padding: 12px 24px; margin: 0 10px; cursor: pointer; font-weight: bold; border: none; border-radius: 6px; font-size: 16px; color: white; }}
        .btn-jpg {{ background-color: #ff4b4b; }}
        .btn-pdf {{ background-color: #0071e3; }}

        /* 打印时隐藏按钮，消除边距 */
        @media print {{
            .toolbar {{ display: none !important; }}
            body {{ background-color: white; padding: 0; }}
            #quote-paper {{ box-shadow: none !important; margin: 0 !important; width: 100% !important; }}
        }}

        /* 报价单白纸实体 */
        #quote-paper {{
            width: 860px; background-color: white; padding: 40px 50px; margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); box-sizing: border-box; color: #000;
        }}
        
        .main-title {{ text-align: left; font-size: 26px; font-weight: bold; font-family: "KaiTi", "Kaiti SC", serif; letter-spacing: 2px; margin-bottom: 10px; margin-left: 10%; font-style: italic; }}
        
        /* 严格还原您截图的表头网格对齐 */
        .header-grid {{ display: flex; justify-content: space-between; font-size: 15px; font-weight: bold; line-height: 1.6; margin-bottom: 10px; }}
        
        /* 表格样式 */
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 0; }}
        th, td {{ border: 1.5px solid #000; padding: 6px 2px; height: 26px; }}
        
        .bg-blue {{ background-color: #00BFFF !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .text-red-box {{ color: red; font-weight: bold; text-align: center; padding: 8px; border: 1.5px solid #000; border-top: none; font-size: 14px; }}
        .bg-yellow-box {{ background-color: #FFFF00 !important; color: red; font-weight: bold; text-align: left; padding: 8px 10px; border: 1.5px solid #000; border-top: none; font-size: 13px; line-height: 1.6; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
        .total-row {{ border: 1.5px solid #000; border-top: none; padding: 6px 10px; display: flex; justify-content: space-between; font-weight: bold; font-size: 15px; }}
    </style>
</head>
<body>

    <div class="toolbar">
        <button class="btn btn-jpg" onclick="exportJPG()">📸 导出高清 JPG</button>
        <button class="btn btn-pdf" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
    </div>

    <div id="quote-paper">
        <div class="main-title">浙江西州将军门业有限公司</div>
        
        <div class="header-grid">
            <div style="width: 55%;">
                <div>致：{customer}</div>
                <div>项目名称：{project}</div>
                <div>启：</div>
            </div>
            <div style="width: 40%;">
                <div>日期：{date_str}</div>
                <div>传真：{fax}</div>
                <div>主题：{subject}</div>
            </div>
        </div>
        
        <div style="font-style: italic; font-weight: bold; font-size: 14px; margin-bottom: 10px; letter-spacing: 1px;">
            承蒙关照，感谢贵方对我方产品感兴趣，根据贵方要求，报上我公司价格，可随时来电来函告知，我们将及时为您提供。
        </div>

        <table>
            <tr>
                <th rowspan="2" width="5%" style="color: darkblue;">序号</th>
                <th rowspan="2" width="30%" style="color: darkblue;">品名型号</th>
                <th colspan="2" width="15%" style="color: darkblue;">规格</th>
                <th rowspan="2" width="8%" style="color: darkblue;">开启方向</th>
                <th rowspan="2" width="5%" style="color: darkblue;">单位</th>
                <th rowspan="2" width="10%" style="color: darkblue;">数量</th>
                <th rowspan="2" width="10%" style="color: darkblue;">单价</th>
                <th rowspan="2" width="12%" style="color: darkblue;">总金额/元</th>
            </tr>
            <tr><th style="color: darkblue;">长</th><th style="color: darkblue;">宽</th></tr>
            
            {rows_html}
            
            <tr class="bg-blue">
                <td colspan="8" style="text-align: left; padding-left: 10px;">合计</td>
                <td>{grand_total}</td>
            </tr>
        </table>
        
        <div class="text-red-box">本报价为含税工厂结算价，不含木箱。如要木箱包装，另加100元一平方</div>
        
        <div class="total-row">
            <span>合计总金额（大写）：</span>
            <span style="letter-spacing: 2px;">{total_upper}</span>
        </div>
        
        <div class="bg-yellow-box">
            1. 付款方式: 确定制作，先安排货款50%的定金，款清发货<br>
            2. 以上价格不包含运费、安装调试费、测量等费用。<br>
            3. 请及时确定签字回传，我司以收到贵方签字回传单以及保证金为准，方可安排生产<br>
            <hr style="border:
