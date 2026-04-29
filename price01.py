import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

st.set_page_config(page_title="西州将军门业 - 智能报价系统", layout="wide")

# 1. 自动读取或生成产品库
if not os.path.exists("library.csv"):
    # 如果没找到 csv，自动建一个默认的，防止报错
    default_data = pd.DataFrame({
        "name": ["0.8的纯铜两定两开门", "门柱花件另加", "暗合页（子母）"],
        "unit": ["m²", "m²", "套"],
        "price": [6000, 2750, 1000]
    })
    default_data.to_csv("library.csv", index=False)

df_library = pd.read_csv("library.csv")
# 将表格数据转为 JSON 格式，方便前端 JavaScript 使用
library_json = df_library.to_dict(orient="records")
product_options = "".join([f'<option value="{row["name"]}">{row["name"]}</option>' for _, row in df_library.iterrows()])

# 2. 生成今天的日期
today_str = datetime.today().strftime('%Y.%m.%d')

# 3. 核心：1:1 响应式 HTML/JS 模板
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        /* 隐藏滚动条和全局背景 */
        body {{ background-color: #f0f2f6; font-family: "SimSun", "Songti SC", serif; margin: 0; padding: 20px; }}
        
        /* 打印时隐藏按钮 */
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background-color: white; padding: 0; }}
            #quote-paper {{ box-shadow: none !important; margin: 0 !important; width: 100% !important; }}
        }}

        /* 按钮样式 */
        .btn-group {{ text-align: center; margin-bottom: 20px; }}
        .btn {{ padding: 10px 20px; margin: 0 10px; cursor: pointer; font-weight: bold; border: none; border-radius: 5px; color: white; }}
        .btn-jpg {{ background-color: #ff4b4b; }}
        .btn-pdf {{ background-color: #0071e3; }}

        /* 报价单白纸样式 */
        #quote-paper {{
            width: 850px; background-color: white; padding: 40px; margin: 0 auto;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); box-sizing: border-box;
        }}
        
        /* 表格与无缝输入框样式 (关键：让输入框看起来像普通文字) */
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 14px; margin-top: 15px; }}
        th, td {{ border: 1.5px solid black; padding: 6px; }}
        
        input, select {{
            width: 100%; border: none; background: transparent; text-align: center;
            font-family: inherit; font-size: inherit; outline: none; padding: 0;
        }}
        /* 当鼠标悬浮或点击时，给一点点提示，暗示可编辑 */
        input:hover, select:hover {{ background-color: #f9f9f9; cursor: pointer; }}
        input:focus, select:focus {{ background-color: #e6f7ff; }}
        
        /* 左对齐的输入框 */
        .text-left {{ text-align: left; }}
        
        /* 颜色区块还原 */
        .bg-blue {{ background-color: #00BFFF !important; font-weight: bold; }}
        .text-red {{ color: red; font-weight: bold; padding: 10px; border: 1.5px solid black; border-top: none; text-align: center; }}
        .bg-yellow {{ background-color: #FFFF00 !important; color: red; font-weight: bold; padding: 10px; border: 1.5px solid black; border-top: none; font-size: 13px; text-align: left; line-height: 1.6; }}
    </style>
</head>
<body>

    <div class="btn-group no-print">
        <button class="btn btn-jpg" onclick="exportJPG()">📸 导出高清 JPG</button>
        <button class="btn btn-pdf" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
    </div>

    <div id="quote-paper">
        <h2 style="text-align: center; letter-spacing: 2px;">浙江西州将军门业有限公司</h2>
        
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-weight: bold;">
            <div style="width: 60%;">
                致：<input type="text" value="张仕玉" style="width: 200px; text-align: left; font-weight: bold;"> <br>
                项目名称：<input type="text" value="龙井村322号" style="width: 200px; text-align: left;"> <br>
                启：<input type="text" style="width: 200px; text-align: left;">
            </div>
            <div style="width: 35%;">
                日期：<input type="text" value="{today_str}" style="width: 150px; text-align: left;"> <br>
                传真：<input type="text" style="width: 150px; text-align: left;"> <br>
                主题：<input type="text" style="width: 150px; text-align: left;">
            </div>
        </div>
        
        <div style="font-style: italic; font-weight: bold; font-size: 14px;">
            承蒙关照，感谢贵方对我方产品感兴趣，根据贵方要求，报上我公司价格，可随时来电来函告知，我们将及时为您提供。
        </div>

        <table>
            <tr>
                <th rowspan="2" width="5%">序号</th>
                <th rowspan="2" width="25%">品名型号</th>
                <th colspan="2" width="20%">规格</th>
                <th rowspan="2" width="8%">开启方向</th>
                <th rowspan="2" width="7%">单位</th>
                <th rowspan="2" width="10%">数量</th>
                <th rowspan="2" width="10%">单价</th>
                <th rowspan="2" width="15%">总金额/元</th>
            </tr>
            <tr><th>长</th><th>宽</th></tr>
            
            <tr>
                <td>1</td>
                <td class="text-left">
                    <select id="prod_1" onchange="updateRow(1)">
                        <option value="">-- 手动输入或选择 --</option>
                        {product_options}
                    </select>
                    <input type="text" id="desc_1" placeholder="规格补充描述..." class="text-left" style="font-size: 12px; margin-top: 4px;">
                </td>
                <td><input type="number" id="l_1" value="2480" oninput="calcTotal()"></td>
                <td><input type="number" id="w_1" value="2690" oninput="calcTotal()"></td>
                <td><select><option>内右开</option><option>内左开</option><option>外右开</option><option>外左开</option></select></td>
                <td><input type="text" id="unit_1" value="m²"></td>
                <td><input type="number" id="qty_1" value="6.6712" step="0.0001" oninput="calcTotal()"></td>
                <td><input type="number" id="price_1" value="6000" oninput="calcTotal()"></td>
                <td id="total_1" style="font-weight: bold;">40027</td>
            </tr>
            
            <tr>
                <td>2</td>
                <td><input type="text" class="text-left"></td>
                <td><input type="number"></td><td><input type="number"></td><td><input type="text"></td>
                <td><input type="text" id="unit_2"></td>
                <td><input type="number" id="qty_2" value="0" oninput="calcTotal()"></td>
                <td><input type="number" id="price_2" value="0" oninput="calcTotal()"></td>
                <td id="total_2">0</td>
            </tr>
            
            <tr class="bg-blue">
                <td colspan="8" style="text-align: left; padding-left: 10px;">合计</td>
                <td id="grand_total">40027</td>
            </tr>
        </table>
        
        <div class="text-red">本报价为含税工厂结算价，不含木箱。如要木箱包装，另加100元一平方</div>
        
        <div style="padding: 8px 10px; border: 1.5px solid black; border-top: none; display: flex; justify-content: space-between; font-weight: bold;">
            <span>合计总金额（大写）：</span>
            <span id="grand_total_chinese" style="letter-spacing: 2px;">肆万零贰拾柒元整</span>
        </div>
        
        <div class="bg-yellow">
            1. 付款方式: 确定制作，先安排货款50%的定金，款清发货<br>
            2. 以上价格不包含运费、安装调试费、测量等费用。<br>
            3. 请及时确定签字回传，我司以收到贵方签字回传单以及保证金为准，方可安排生产<br>
            <hr style="border: 0.5px solid red; margin: 5px 0;">
            开票资料: 对公账户公司名称杭州浙家门业有限公司账户<br>
            号码: 3301041060000451769<br>
            开户银行: 杭州银行富阳支行<br>
            <hr style="border: 0.5px solid red; margin: 5px 0;">
            汇款请汇入以下账户<br>
            户名：张春兰<br>
            账号：622848 0329 2739 08775<br>
            汇款行农业银行浙江省分行杭州市上泗支行
        </div>
    </div>

    <script>
        // 获取 Python 传过来的产品库
        const db = {json.dumps(library_json, ensure_ascii=False)};

        // 联动逻辑：当下拉框选择产品时，自动填充单位和单价
        function updateRow(rowIdx) {{
            const selectedName = document.getElementById('prod_' + rowIdx).value;
            const product = db.find(p => p.name === selectedName);
            if (product) {{
                document.getElementById('unit_' + rowIdx).value = product.unit;
                document.getElementById('price_' + rowIdx).value = product.price;
                calcTotal(); // 触发重新计算
            }}
        }}

        // 计算逻辑：实时计算总价和大写
        function calcTotal() {{
            let grandTotal = 0;
            // 遍历所有行
            for(let i=1; i<=2; i++) {{
                let qty = parseFloat(document.getElementById('qty_' + i).value) || 0;
                let price = parseFloat(document.getElementById('price_' + i).value) || 0;
                let rowTotal = Math.round(qty * price); // 四舍五入取整
                document.getElementById('total_' + i).innerText = rowTotal;
                grandTotal += rowTotal;
            }}
            document.getElementById('grand_total').innerText = grandTotal;
            document.getElementById('grand_total_chinese').innerText = numberToChinese(grandTotal);
        }}

        // 数字转大写函数
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

        // 导出 JPG 逻辑
        function exportJPG() {{
            const target = document.getElementById('quote-paper');
            html2canvas(target, {{ scale: 2, useCORS: true }}).then(canvas => {{
                const link = document.createElement('a');
                link.download = '西州将军报价单.jpg';
                link.href = canvas.toDataURL('image/jpeg', 1.0);
                link.click();
            }});
        }}
        
        // 页面加载完成时计算一次初始值
        window.onload = calcTotal;
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=950, scrolling=True)

st.caption("提示：鼠标点击表单中的文字或数字即可直接修改。点击『品名型号』下拉框可联动数据库中的价格。")
