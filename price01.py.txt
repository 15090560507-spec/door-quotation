import streamlit as st
import base64
from PIL import Image
from io import BytesIO

# --- 1. 页面配置 (Apple 简约风格) ---
st.set_page_config(page_title="西州将军门业报价系统", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    .stButton>button { border-radius: 8px; width: 100%; background-color: #0071e3; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 辅助函数：数字转人民币大写 ---
def to_rmb_upper(num):
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整" if res else "零元整"

# --- 3. 侧边栏输入 (数据驱动) ---
with st.sidebar:
    st.header("📝 报价信息录入")
    customer = st.text_input("客户名称 (致)", "张仕玉")
    project = st.text_input("项目名称", "龙井村322号")
    date_str = st.date_input("日期").strftime("%Y.%m.%d")
    
    st.divider()
    product = st.text_input("品名型号", "0.8的纯铜两定两开门")
    col1, col2 = st.columns(2)
    with col1:
        length = st.number_input("长 (mm)", value=2480)
        price = st.number_input("单价", value=6000)
    with col2:
        width = st.number_input("宽 (mm)", value=2690)
        qty = st.number_input("数量 (m²)", value=6.6712, format="%.4f")
    
    total = round(qty * price, 0)
    total_upper = to_rmb_upper(total)

# --- 4. 透明图层覆盖逻辑 (HTML/CSS) ---
# 读取本地底图并转为 Base64 (确保 static 文件夹下有 background.png)
try:
    img = Image.open("static/background.png")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
except FileNotFoundError:
    st.error("请在 static 文件夹中放入名为 background.png 的报价单底图")
    st.stop()

# 定义 1:1 还原的 HTML 模板
# 注意：下面的 top 和 left 坐标需要根据你底图的实际像素进行微调
html_template = f"""
<div id="quotation-container" style="position: relative; width: 850px; margin: auto; background-color: white;">
    <img src="data:image/png;base64,{img_base64}" style="width: 100%; display: block;">
    
    <div style="position: absolute; top: 11.5%; left: 8%; font-size: 16px; font-weight: bold;">{customer}</div>
    <div style="position: absolute; top: 13.5%; left: 8%; font-size: 14px;">{project}</div>
    <div style="position: absolute; top: 11.5%; left: 78%; font-size: 14px;">{date_str}</div>
    
    <div style="position: absolute; top: 28%; left: 10%; font-size: 13px; width: 30%; text-align: left;">{product}</div>
    <div style="position: absolute; top: 28%; left: 43%; font-size: 13px;">{length}</div>
    <div style="position: absolute; top: 28%; left: 51%; font-size: 13px;">{width}</div>
    <div style="position: absolute; top: 28%; left: 68%; font-size: 13px;">{qty}</div>
    <div style="position: absolute; top: 28%; left: 78%; font-size: 13px;">{price}</div>
    <div style="position: absolute; top: 28%; left: 88%; font-size: 13px;">{int(total)}</div>
    
    <div style="position: absolute; top: 48%; left: 88%; font-size: 15px; font-weight: bold;">{int(total)}</div>
    <div style="position: absolute; top: 56%; left: 30%; font-size: 16px; font-weight: bold; letter-spacing: 5px;">{total_upper}</div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadJPG() {{
    const container = document.getElementById('quotation-container');
    html2canvas(container, {{ scale: 2 }}).then(canvas => {{
        const link = document.createElement('a');
        link.download = '报价单_{customer}.jpg';
        link.href = canvas.toDataURL('image/jpeg', 0.9);
        link.click();
    }});
}}
</script>
"""

# 渲染预览
st.components.v1.html(html_template + '<div style="height: 50px;"></div>', height=1000, scrolling=True)

# 导出按钮
if st.button("📸 生成高清报价单图片 (JPG)"):
    st.components.v1.html("<script>downloadJPG();</script>", height=0)