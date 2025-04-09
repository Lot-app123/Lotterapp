
from flask import Flask, render_template, request, send_file
from flask_login import login_required
from io import BytesIO
import os
import random
from PIL import Image, ImageDraw, ImageFont
import zipfile

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/", methods=["GET", "POST"])
@login_required
def lottery():
    if request.method == "POST":
        lottery_types = request.form.getlist("lottery_type")
        bg_choice = request.form.get("bg_choice")
        images = []

        for lottery_type in lottery_types:
            img_bytes = create_image(lottery_type, bg_choice)
            images.append((lottery_type, img_bytes))

        if len(images) == 1:
            return send_file(images[0][1], mimetype="image/png", as_attachment=True, download_name=f"{images[0][0]}.png")

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for lottery_type, img_bytes in images:
                zipf.writestr(f"{lottery_type}.png", img_bytes.read())
                img_bytes.seek(0)
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="lottery_results.zip")

    return render_template("index copy.html")

def create_image(lottery_type, bg_choice):
    bg_path = os.path.join("static", bg_choice)
    font_path = os.path.join("static", "Mali-Bold.ttf")

    image = Image.open(bg_path).convert("RGB")
    image = image.resize((1280, 720))

    draw = ImageDraw.Draw(image)
    font_large = ImageFont.truetype(font_path, 100)
    font_medium = ImageFont.truetype(font_path, 70)
    font_small = ImageFont.truetype(font_path, 40)

    bbox = draw.textbbox((0, 0), lottery_type, font=font_medium)
    text_width = bbox[2] - bbox[0]
    x_position = (image.width - text_width) // 2
    draw.text((x_position, 50), lottery_type, font=font_medium, fill="white")

    num1, num2 = random.sample(range(0, 10), 2)
    base_tens = random.sample([f"{num1}{i}" for i in range(10)], 10)
    base_units = random.sample([f"{num2}{i}" for i in range(10)], 10)

    tens1, tens2, tens3 = base_tens[:4], base_tens[4:7], base_tens[7:]
    units1, units2, units3 = base_units[:4], base_units[4:7], base_units[7:]

    random_6_digits = "".join(random.choices(f"{num1}{num2}" + "0123456789", k=6))

    draw.text((350, 250), f"{num1} - {num2}", font=font_large, fill="yellow")
    draw.text((250, 350), " ".join(tens1), font=font_small, fill="yellow")
    draw.text((250, 400), " ".join(units1), font=font_small, fill="yellow")
    draw.text((300, 500), f"วิน.{random_6_digits}", font=font_medium, fill="yellow")

    output_io = BytesIO()
    image.save(output_io, format="PNG", optimize=True)
    output_io.seek(0)

    return output_io

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
