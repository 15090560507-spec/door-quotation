import streamlit as st
import pandas as pd
import openpyxl
from io import BytesIO
from datetime import datetime
import os

st.set_page_config(page_title="西州将军门业 - 自动化报价系统", layout="wide")

# ==========================================
# 1. 读取数据库
# ==========================================
if not os.path.exists("library.csv"):
    st.error("找不到 library.csv 产品库文件！")
    st.stop()

df_library = pd.read_csv("library.csv")
product_names = df_library['name'].tolist()

# ==========================================
# 2. 网页控制面板 (极简数据录入)
# ==========================================
st.title("📊 西州门业报价单生成器 (直控 Excel 版)")
st.markdown("在这里输入数据，系统将自动注入到您的专属 Excel 模板中，保证 100% 格式无损。")

with st.expander("📝 第一步：基础信息", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        customer = st.text_input("客户名称 (致)", "张仕玉")
    with col2:
        project = st.text_input("项目名称", "龙井村322号")
    with col3:
        date_str = st.date_input("日期").strftime("%Y.%m.%d")

with st.expander("🛒 第二步：产品明细", expanded=True):
    # 第一行产品
    st.markdown("**产品 1**")
    col_p1, col_l1, col_w1, col_qty1 = st.columns([3, 1, 1, 1])
    with col_p1:
        prod_1 = st.selectbox("选择型号", [""] + product_names, key="p1")
    with col_l1:
        l_1 = st.number_input("长(mm)", value=2480, key="l1")
    with col_w1:
        w_1 = st.number_input("宽(mm)", value=2690, key="w1")
    with col_qty1:
        qty_1 = st.number_input("数量", value=6.6712, format="%.4f", key="q1")
    
    # 自动带出单价和计算
    price_1 = 0
    if prod_1:
        price_1 = df_library[df_library['name'] == prod_1]['price'].values[0]
    total_1 = round(qty_1 * price_1)
    
    if prod_1:
        st.info(f"系统已自动带出单价：**{price_1}** 元，此行小计：**{total_1}** 元")

# 计算总金额
grand_total = total_1 # 如果有多行，这里累加
st.subheader(f"💰 当前总计：{grand_total} 元")

# ==========================================
# 3. 后台操控 Excel 核心逻辑
# ==========================================
# 数字转大写函数
def numberToChinese(num):
    # (此处省略大写转换代码，可以使用前面提供的，或者让Excel自带宏计算)
    d = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    u = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    s = str(int(num))
    res = ''.join([d[int(s[i])] + u[len(s)-i-1] for i in range(len(s)) if s[i] != '0' or (len(s)-i-1) % 4 == 0]).replace('零零', '零').replace('零万', '万').replace('零亿', '亿')
    return res.rstrip('零') + "元整" if res else "零元整"

if st.button("🚀 一键注入并下载 Excel 报价单", type="primary"):
    if not os.path.exists("template.xlsx"):
        st.error("找不到 template.xlsx 模板文件！请将空白模板与代码放在一起。")
    else:
        try:
            # 打开真正的 Excel 模板
            wb = openpyxl.load_workbook("template.xlsx")
            sheet = wb.active
            
            # --- 精准注入数据 ---
            # ⚠️ 注意：这里的单元格坐标（如 B3, C10）必须根据你真实的 template.xlsx 进行修改！
            sheet['B3'] = customer       # 假设致客户在 B3
            sheet['B4'] = project        # 项目名称
            sheet['L3'] = date_str       # 日期
            
            # 注入产品 1 (假设第一行数据在第 10 行)
            if prod_1:
                sheet['C10'] = prod_1
                sheet['G10'] = l_1
                sheet['I10'] = w_1
                sheet['M10'] = qty_1
                sheet['N10'] = price_1
                sheet['O10'] = total_1
            
            # 注入合计和大写 (假设在 17, 20 行)
            sheet['O17'] = grand_total
            sheet['D20'] = numberToChinese(grand_total)
            
            # 保存到内存
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            st.success("✅ Excel 注入成功！请点击下方按钮下载：")
            st.download_button(
                label="📥 下载西州门业报价单.xlsx",
                data=output,
                file_name=f"报价单_{customer}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"处理 Excel 时出错：{e}")
