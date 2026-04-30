import streamlit as st
import pandas as pd
from datetime import datetime
import json

# --- 1. 页面级高级配置 ---
st.set_page_config(page_title="西州将军门业 - 尊贵级报价系统", layout="wide")

# 加载自定义 CSS 以实现 Apple 式简约质感
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    .stButton>button { border-radius: 8px; width: 100%; height: 45px; background-color: #0071e3; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #0077ed; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 数据库逻辑 ---
@st.cache_data
def load_db():
    # 模拟从 library.csv 读取，若不存在则创建
    return pd.DataFrame({
        "name": ["0.8的纯铜两定两开门", "0.8的不锈钢镀铜:正面1.2mm镀铜蚀刻", "暗合页（子母）", "门柱花件另加"],
        "unit": ["m²", "m²", "套", "m²"],
        "price": [6000, 1680, 1000, 2750]
    })

df_lib = load_db()

# --- 3. 业务逻辑：人民币大写转换 ---
def to_chinese_upper(num):
    if num == 0: return "零元整"
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整"

# --- 4. 侧边栏：核心数据录入 ---
st.sidebar.header("🏺 尊贵定制录入")
customer = st.sidebar.text_input("致 (客户名称)", "张仕玉")
project = st.sidebar.text_input("项目名称", "龙井村322号")
date_str = st.sidebar.date_input("日期", datetime.today()).strftime("%Y.%m.%d")

# --- 5. 多行动态加项逻辑 ---
st.subheader("🛠️ 产品明细与工程参数")

if 'rows' not in st.session_state:
    st.session_state.rows = pd.DataFrame([{
        "品名型号": "0.8的纯铜两定两开门", "长_mm": 2480, "宽_mm": 2690, 
        "开启方向": "外右开", "单位": "m²", "数量": 6.6712, "单价": 6000.0
    }])

edited_df = st.data_editor(
    st.session_state.rows,
    num_rows="dynamic",
    column_config={
        "品名型号": st.column_config.SelectboxColumn("品名型号", options=df_lib['name'].tolist(), required=True),
        "开启方向": st.column_config.SelectboxColumn("开启方向", options=["外右开", "内右开", "外左开", "内左开", ""]),
        "数量": st.column_config.NumberColumn("数量", format="%.4f"),
        "单价": st.column_config.NumberColumn("单价", format="%.2f")
    },
    use_container_width=True
)

# 自动计算金额
edited_df['总金额'] = (edited_df['数量'] * edited_df['单价']).round(0).fillna(0).astype(int)
grand_total = int(edited_df['总金额'].sum())
total_upper = to_chinese_upper(grand_total)

# --- 6. 1:1 高清渲染模板 ---
st.divider()

rows_html = ""
for i, row in edited_df.iterrows():
    rows_html += f"""
    <tr>
        <td>{i+1}</td>
        <td style="text-align:left; font-weight:bold;">{row['品名型号']}</td>
        <td>{row['长_mm']}</td><td>{row['宽_mm']}</td>
        <td>{row['开启方向']}</td><td>{row['单位']}</td>
        <td>{row['数量']}</td><td>{row['单价']}</td>
        <td style="font-weight:bold;">{row['总金额']}</td>
    </tr>
    """

# 补齐视觉空行
for i in range(len(edited_df), 4):
    rows_html += "<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td><td></td><td>0.0000</td><td>0</td><td>0</td></tr>"

html_output = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        #paper {{ width: 840px; background: white; padding: 45px; margin: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.1); font-family: "STSong", "SimSun", serif; color: #000; position: relative; }}
        .title {{ text-align: left; font-size: 26px; font-weight: bold; margin-bottom: 20px; font-family: "KaiTi", serif; letter-spacing: 3px; font-style: italic; margin-left: 50px; }}
        .header-box {{ display: flex; justify-content: space-between; font-size: 15px; font-weight: bold; line-height: 1.8; }}
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; margin-top: 15px; border: 1.5px solid black; }}
        th, td {{ border: 1.2px solid black; padding: 7px 2px; }}
        .bg-blue {{ background-color: #00BFFF !important; font-weight: bold; }}
        .bg-yellow {{ background-color: #FFFF00 !important; color: red; font-weight: bold; text-align: left; padding: 10px; font-size: 12px; line-height: 1.6; border: 1.5px solid black; border-top: none; }}
        .red-note {{ color: red; font-weight: bold; text-align: center; border: 1.5px solid black; border-top: none; padding: 8px; font-size: 14px; }}
    </style>
</head>
<body>
    <div id="paper">
        <div class="title">浙江西州将军门业有限公司</div>
        <div class="header-box">
            <div>致：{customer}<br>项目名称：{project}<br>启：</div>
            <div style="text-align:right;">日期：{date_str}<br>传真：<br>主题：</div>
        </div>
        <div style="font-style:italic; font-weight:bold; font-size:14px; margin: 10px 0;">承蒙关照，感谢贵方对我方产品感兴趣...我们将及时为您提供。</div>
        <table>
            <tr><th rowspan="2">序号</th><th rowspan="2" width="30%">品名型号</th><th colspan="2">规格</th><th rowspan="2">开启方向</th><th rowspan="2">单位</th><th rowspan="2">数量</th><th rowspan="2">单价</th><th rowspan="2">总金额</th></tr>
            <tr><th>长</th><th>宽</th></tr>
            {rows_html}
            <tr class="bg-blue"><td colspan="8" style="text-align:left; padding-left:10px;">合计</td><td>{grand_total}</td></tr>
        </table>
        <div class="red-note">本报价为含税工厂结算价，不含木箱。如要木箱包装，另加100元一平方</div>
        <div style="border:1.5px solid black; border-top:none; padding:8px; font-weight:bold;">合计总金额 (大写): <span style="margin-left:50px; letter-spacing: 2px;">{total_upper}</span></div>
        <div class="bg-yellow">
            1. 付款方式: 确定制作，先安排货款50%的定金，款清发货<br>
            2. 以上价格不包含运费、安装调试费、测量等费用。<br>
            汇款账号：张春兰 622848 0329 2739 08775 (农业银行浙江省分行)
        </div>
    </div>
    <script>
        function saveAsJPG() {{
            const target = document.getElementById('paper');
            html2canvas(target, {{ scale: 2.5 }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '西州报价单_{customer}.jpg';
                link.href = canvas.toDataURL('image/jpeg', 1.0);
                link.click();
            }});
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_output, height=1000, scrolling=True)

if st.button("📸 导出高清尊贵版报价单 (JPG)"):
    st.components.v1.html("<script>saveAsJPG();</script>", height=0)
