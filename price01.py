import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# 1. 页面基础配置
# ==========================================
st.set_page_config(page_title="西州将军门业 - 智能报价系统", layout="wide")

# ==========================================
# 2. 读取报价库 (数据驱动)
# ==========================================
# 尝试读取同目录下的 library.csv，如果没有会自动生成一个演示用的
if not os.path.exists("library.csv"):
    pd.DataFrame({
        "name": ["0.8的纯铜两定两开门", "门柱花件另加"],
        "unit": ["m²", "m²"],
        "price": [6000, 2750]
    }).to_csv("library.csv", index=False)

df_library = pd.read_csv("library.csv")
# 将 Python 数据转为 JSON，传给前端 JavaScript
library_json = df_library.to_dict(orient="records")
# 生成前端下拉框的 HTML 代码
product_options = "".join([f'<option value="{row["name"]}">{row["name"]}</option>' for _, row in df_library.iterrows()])

today_str = datetime.today().strftime('%Y.%m.%d')

# ==========================================
# 3. 核心：1:1 像素级 HTML 与 JS 控制台
# ==========================================
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        /* 全局网页背景（仅在网页看得到，不被导出） */
        body {{ background-color: #e0e5ec; font-family: "SimSun", "STSong", serif; margin: 0; padding: 20px; }}
        
        /* 打印和导出时的特殊控制 */
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background-color: white; padding: 0; }}
            #quote-paper {{ box-shadow: none !important; margin: 0 !important; width: 100% !important; }}
        }}

        /* 顶部操作按钮 */
        .toolbar {{ text-align: center; margin-bottom: 20px; }}
        .btn {{ padding: 12px 24px; margin: 0 10px; cursor: pointer; font-weight: bold; border: none; border-radius: 6px; font-size: 16px; color: white; transition: 0.2s; }}
        .btn-jpg {{ background-color: #ff4b4b; }}
        .btn-pdf {{ background-color: #0071e3; }}
        .btn:hover {{ filter: brightness(1.1); transform: translateY(-1px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}

        /* --- 报价单白纸样式 (核心排版区) --- */
        #quote-paper {{
            width: 860px; /* 模拟 A4 纸宽度 */
            background-color: white; 
            padding: 40px 50px; 
            margin: 0 auto;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15); /* 高级阴影感 */
            box-sizing: border-box;
            color: #000;
        }}
        
        .main-title {{ text-align: left; font-size: 26px; font-weight: bold; font-family: "KaiTi", "Kaiti SC", serif; letter-spacing: 2px; margin-bottom: 10px; margin-left: 10%; font-style: italic; }}
        
        /* 表头信息网格 */
        .info-grid {{ display: flex; justify-content: space-between; font-size: 15px; font-weight: bold; line-height: 1.8; margin-bottom: 10px; }}
        
        /* 无缝输入框：让输入框看起来就是普通文字 */
        input, select {{
            border: none; background: transparent; font-family: inherit; font-size: inherit; font-weight: inherit; outline: none; padding: 0; margin: 0;
        }}
        /* 交互提示：鼠标悬停时轻微变色，暗示可编辑 */
        input:hover, select:hover {{ background-color: rgba(0, 113, 227, 0.05); cursor: text; }}
        
        /* 表格样式严格复刻 Excel */
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; font-weight: bold; margin-bottom: 0; }}
        th, td {{ border: 1.5px solid #000; padding: 6px 4px; height: 28px; }}
        
        .col-qty, .col-price {{ text-align: right; padding-right: 5px; }}
        
        /* 特定颜色块复刻 */
        .bg-blue {{ background-color: #00BFFF !important; }}
        .text-red-box {{ color: red; font-weight: bold; text-align: center; padding: 8px; border: 1.5px solid #000; border-top: none; font-size: 14px; }}
        .bg-yellow-box {{ background-color: #FFFF00 !important; color: red; font-weight: bold; text-align: left; padding: 8px 10px; border: 1.5px solid #000; border-top: none; font-size: 13px; line-height: 1.5; }}
        
        .total-row {{ border: 1.5px solid #000; border-top: none; padding: 6px 10px; display: flex; justify-content: space-between; font-weight: bold; }}
    </style>
</head>
<body>

    <div class="toolbar no-print">
        <button class="btn btn-jpg" onclick="exportJPG()">📸 导出高清 JPG</button>
        <button class="btn btn-pdf" onclick="window.print()">🖨️ 直接打印 / 存为 PDF</button>
        <p style="color: #666; font-size: 14px; margin-top: 10px;">提示：直接点击下方表格中的文字即可修改。下拉选择型号可自动填充单价。</p>
    </div>

    <div id="quote-paper">
        <div class="main-title">浙江西州将军门业有限公司</div>
        
        <div class="info-grid">
            <div style="width: 55%;">
                致：<input type="text" value="张仕玉" style="width: 250px; border-bottom: 1px solid #ddd;"><br>
                项目名称：<input type="text" value="龙井村322号" style="width: 200px;"><br>
                启：<input type="text" style="width: 200px;">
            </div>
            <div style="width: 40%;">
                日期：<input type="text" value="{today_str}" style="width: 150px;"><br>
                传真：<input type="text" style="width: 150px;"><br>
                主题：<input type="text" style="width: 150px;">
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
            
            <tr>
                <td>1</td>
                <td style="text-align: left;">
                    <select id="prod_1" onchange="updateRow(1)" style="width: 100%;">
                        <option value="">-- 手动输入或下拉选择 --</option>
                        {product_options}
                    </select>
                </td>
                <td><input type="number" id="l_1" value="2480" style="width:100%; text-align:center;"></td>
                <td><input type="number" id="w_1" value="2690" style="width:100%; text-align:center;"></td>
                <td><select><option></option><option>内右开</option><option>内左开</option><option>外右开</option><option>外左开</option></select></td>
                <td><input type="text" id="unit_1" style="width:100%; text-align:center;"></td>
                <td><input type="number" id="qty_1" value="6.6712" step="0.0001" oninput="calcTotal()" style="width:100%; text-align:center;"></td>
                <td><input type="number" id="price_1" oninput="calcTotal()" style="width:100%; text-align:center;"></td>
                <td id="total_1">0</td>
            </tr>
            
            <tr>
                <td>2</td>
                <td><input type="text" style="width: 100%;"></td>
                <td><input type="number" style="width:100%; text-align:center;"></td>
                <td><input type="number" style="width:100%; text-align:center;"></td>
                <td><input type="text" style="width:100%; text-align:center;"></td>
                <td><input type="text" style="width:100%; text-align:center;"></td>
                <td><input type="number" id="qty_2" value="0" oninput="calcTotal()" style="width:100%; text-align:center;"></td>
                <td><input type="number" id="price_2" value="0" oninput="calcTotal()" style="width:100%; text-align:center;"></td>
                <td id="total_2">0</td>
            </tr>
            <tr><td></td><td></td><td></td><td></td><td></td><td></td><td><input type="number" id="qty_3" value="0" style="opacity:0;"></td><td><input type="number" id="price_3" value="0" style="opacity:0;"></td><td id="total_3">0</td></tr>
            <tr><td></td><td></td><td></td><td></td><td></td><td></td><td><input type="number" id="qty_4" value="0" style="opacity:0;"></td><td><input type="number" id="price_4" value="0" style="opacity:0;"></td><td id="total_4">0</td></tr>
            
            <tr class="bg-blue">
                <td colspan="8" style="text-align: left; padding-left: 10px;">合计</td>
                <td id="grand_total">0</td>
            </tr>
        </table>
        
        <div class="text-red-box">本报价为含税工厂结算价，不含木箱。如要木箱包装，另加100元一平方</div>
        
        <div class="total-row">
            <span>合计总金额（大写）：</span>
            <span id="grand_total_chinese" style="letter-spacing: 2px;">零元整</span>
        </div>
        
        <div class="bg-yellow-box">
            1. 付款方式: 确定制作，先安排货款50%的定金，款清发货<br>
            2. 以上价格不包含运费、安装调试费、测量等费用。<br>
            3. 请及时确定签字回传，我司以收到贵方签字回传单以及保证金为准，方可安排生产<br>
            <hr style="border: 0.5px solid red; margin: 4px 0;">
            开票资料: 对公账户公司名称杭州浙家门业有限公司账户<br>
            号码: 3301041060000451769<br>
            开户银行: 杭州银行富阳支行<br>
            法定代表人: 王家龙基本存款<br>
            账户编号: J3310198780901<br>
            <hr style="border: 0.5px solid red; margin: 4px 0;">
            汇款请汇入以下账户<br>
            户名：张春兰<br>
            账号：622848 0329 2739 08775<br>
            汇款行农业银行浙江省分行杭州市上泗支行
        </div>
    </div>

    <script>
        const db = {json.dumps(library_json, ensure_ascii=False)};

        // 选择产品联动带出单位和单价
        function updateRow(rowIdx) {{
            const selectedName = document.getElementById('prod_' + rowIdx).value;
            const product = db.find(p => p.name === selectedName);
            if (product) {{
                document.getElementById('unit_' + rowIdx).value = product.unit;
                document.getElementById('price_' + rowIdx).value = product.price;
                calcTotal(); // 更新后立刻重算
            }}
        }}

        // 计算逻辑：总价=数量*单价 (四舍五入)
        function calcTotal() {{
            let grandTotal = 0;
            for(let i=1; i<=4; i++) {{
                let qtyEl = document.getElementById('qty_' + i);
                let priceEl = document.getElementById('price_' + i);
                if (qtyEl && priceEl) {{
                    let qty = parseFloat(qtyEl.value) || 0;
                    let price = parseFloat(priceEl.value) || 0;
                    let rowTotal = Math.round(qty * price);
                    document.getElementById('total_' + i).innerText = rowTotal === 0 ? "0" : rowTotal;
                    grandTotal += rowTotal;
                }}
            }}
            document.getElementById('grand_total').innerText = grandTotal;
            document.getElementById('grand_total_chinese').innerText = numberToChinese(grandTotal);
        }}

        // 人民币转大写
        function numberToChinese(n) {{
            if (n === 0) return "零元整";
            const fraction = ['角', '分'];
            const digit = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
            const unit = [['元', '万', '亿'], ['', '拾', '佰', '仟']];
            let s = '';
            for (let i = 0; i < fraction.length; i++) {{ s += (digit[Math.floor(n * 10 * Math.pow(10, i)) % 10] + fraction[i]).replace(/零./, ''); }}
            s = s || '整'; n = Math.floor(n);
            for (let i = 0; i < unit[0].length && n > 0; i++) {{
                let p = '';
                for (let j = 0; j < unit[1].length && n > 0; j++) {{
                    p = digit[n % 10] + unit[1][j] + p;
                    n = Math.floor(n / 10);
                }}
                s = p.replace(/(零.)*零$/, '').replace(/^$/, '零') + unit[0][i] + s;
            }}
            return s.replace(/(零.)*零元/, '元').replace(/(零.)+/g, '零').replace(/^整$/, '零元整');
        }}

        // JPG 导出功能 (scale: 2.5 保证超高清，类似单反拍出来的字迹)
        function exportJPG() {{
            const target = document.getElementById('quote-paper');
            html2canvas(target, {{ scale: 2.5, useCORS: true, backgroundColor: "#ffffff" }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '西州门业报价单_' + new Date().getTime() + '.jpg';
                link.href = canvas.toDataURL('image/jpeg', 1.0);
                link.click();
            }});
        }}

        // 页面打开时自动计算一次第一行的测试数据
        window.onload = function() {{
            updateRow(1); // 初始化时触发一次联动
        }};
    </script>
</body>
</html>
"""

# 在 Streamlit 中渲染这块巨大的画布
st.components.v1.html(html_code, height=1100, scrolling=True)
