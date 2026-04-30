import streamlit as st
import pandas as pd
import openpyxl
from io import BytesIO
from datetime import datetime
import os

# ==========================================
# 1. 页面基础配置 (现代化极简风格)
# ==========================================
st.set_page_config(page_title="西州将军门业 - 自动化报价系统", layout="wide")

st.title("📊 西州门业报价单生成器")
st.markdown("在这里输入数据，系统将自动注入到您的专属 Excel 模板中，保证 100% 格式无损。")

# ==========================================
# 2. 读取产品数据库
# ==========================================
if not os.path.exists("library.csv"):
    st.error("⚠️ 找不到 library.csv 产品库文件！请确保它与代码在同一目录下。")
    st.stop()

df_library = pd.read_csv("library.csv")
product_names = df_library['name'].tolist()

# ==========================================
# 3. 网页控制面板 (数据录入区)
# ==========================================
with st.expander("📝 第一步：基础信息录入", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        customer = st.text_input("客户名称 (致)", placeholder="例如：张仕玉")
    with col2:
        project = st.text_input("项目名称", placeholder="例如：龙井村322号")
    with col3:
        date_str = st.date_input("报价日期").strftime("%Y.%m.%d")

with st.expander("🛒 第二步：产品明细录入", expanded=True):
    st.markdown("**产品明细 (第 1 行)**")
    col_p, col_l, col_w, col_dir, col_qty = st.columns([3, 1, 1, 1, 1])
    
    with col_p:
        prod_name = st.selectbox("选择品名型号", ["-- 请选择产品 --"] + product_names)
    with col_l:
        length = st.number_input("长 (mm)", value=2480, step=10)
    with col_w:
        width = st.number_input("宽 (mm)", value=2690, step=10)
    with col_dir:
        direction = st.selectbox("开启方向", ["内右开", "内左开", "外右开", "外左开"])
    with col_qty:
        qty = st.number_input("数量 (m²)", value=6.6712, format="%.4f")
    
    # 根据产品库自动带出单价
    price = 0
    if prod_name and prod_name != "-- 请选择产品 --":
        price = df_library[df_library['name'] == prod_name]['price'].values[0]
        st.success(f"✅ 已从库中匹配单价：**{price}** 元")

    total_amount = round(qty * price)

# 人民币转大写函数
def numberToChinese(num):
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整" if res else "零元整"

grand_total_chinese = numberToChinese(total_amount)

# ==========================================
# 4. 后台操控 Excel 核心逻辑 (坐标配置区)
# ==========================================
st.divider()
if st.button("🚀 生成真实 Excel 报价单", type="primary", use_container_width=True):
    if not os.path.exists("template.xlsx"):
        st.error("⚠️ 找不到 template.xlsx 模板文件！请将你的空白 Excel 模板上传到同级目录。")
    else:
        try:
            # 打开真正的 Excel 模板
            wb = openpyxl.load_workbook("template.xlsx")
            sheet = wb.active
            
            # ---------------------------------------------------------
            # 🎯 核心修改区：请把下面括号里的坐标，改成你模板里真实的坐标
            # ---------------------------------------------------------
            # 基础信息
            sheet['B3'] = customer       # 客户名称所在的格子 (例如 B3)
            sheet['B4'] = project        # 项目名称所在的格子
            sheet['K3'] = date_str       # 日期所在的格子
            
            # 第一行明细 (假设在第10行)
            if prod_name != "-- 请选择产品 --":
                sheet['C10'] = prod_name     # 品名型号
                sheet['G10'] = length        # 长
                sheet['I10'] = width         # 宽
                sheet['K10'] = direction     # 开启方向
                sheet['M10'] = qty           # 数量
                sheet['N10'] = price         # 单价
                sheet['O10'] = total_amount  # 此行总价
            
            # 底部合计 (假设蓝色合计在第17行，大写在第20行)
            sheet['O17'] = total_amount
            sheet['C20'] = grand_total_chinese
            # ---------------------------------------------------------

            # 保存到内存
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            st.balloons() # 放个气球庆祝一下
            st.success("🎉 Excel 注入成功！排版 100% 完美，请点击下方按钮下载。")
            
            # 下载按钮
            st.download_button(
                label="📥 下载《西州将军门业报价单》.xlsx",
                data=output,
                file_name=f"报价单_{customer}_{date_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"处理 Excel 时发生错误，请检查坐标是否填写正确：{e}")
