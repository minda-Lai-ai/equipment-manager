import os
import pandas as pd
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def export_abnormal_report(row, image_folder="abnormal_images", export_folder="abnormal_exports", log_path="data/abnormal_log.csv"):
    os.makedirs(export_folder, exist_ok=True)

    eid = row.get("設備請購維修編號", "未知設備")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"異常報告_{eid}_{timestamp}"

    # 匯出 PDF
    pdf_path = os.path.join(export_folder, base_name + ".pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="📸 設備異常回報", ln=True)

    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        pdf.multi_cell(0, 10, f"{col}：{row.get(col, '')}")

    photo_list = str(row.get("照片檔名列表", "")).split(",")
    for name in photo_list:
        path = os.path.join(image_folder, name.strip())
        if os.path.exists(path):
            try:
                pdf.image(path, w=100)
            except Exception:
                pass

    pdf.output(pdf_path)

    # 匯出圖片
    image_path = os.path.join(export_folder, base_name + ".png")
    base_image = Image.new("RGB", (800, 1000), "white")
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.load_default()

    y = 20
    draw.text((20, y), "📸 設備異常回報", font=font, fill="black")
    y += 30
    for col in ["回報時間", "主設備", "次設備", "設備請購維修編號", "異常描述", "報告者"]:
        draw.text((20, y), f"{col}：{row.get(col, '')}", font=font, fill="black")
        y += 25

    if photo_list:
        path = os.path.join(image_folder, photo_list[0].strip())
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGB").resize((760, 500))
                base_image.paste(img, (20, y))
            except Exception:
                pass

    base_image.save(image_path)

    # 更新 abnormal_log.csv 備註欄位
    try:
        df = pd.read_csv(log_path)
        match = df[
            (df["設備請購維修編號"] == row.get("設備請購維修編號")) &
            (df["回報時間"] == row.get("回報時間"))
        ]
        if not match.empty:
            idx = match.index[0]
            df.at[idx, "備註"] = f"已匯出：{os.path.basename(pdf_path)}, {os.path.basename(image_path)}"
            df.to_csv(log_path, index=False)
    except Exception as e:
        print(f"⚠️ 無法更新 abnormal_log.csv 備註欄位：{e}")

    return {
        "pdf_path": pdf_path,
        "image_path": image_path
    }
