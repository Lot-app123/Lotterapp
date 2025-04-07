from flask import Flask, render_template, request, send_file, redirect, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from datetime import datetime
import random
import os
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = "your_secret_key"
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

# ตั้งค่า Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # ถ้ายังไม่ได้ล็อกอินให้ redirect ไปที่หน้า login

# จำลอง user
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# ผู้ใช้ตัวอย่าง (ควรใช้ Database จริง)
users = {"admin": {"password": "1234"}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# 🔹 หน้า Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for("lottery"))  # หลังล็อกอินสำเร็จไปที่หน้าสุ่มหวย
        
    return render_template("login.html")

# 🔹 หน้า Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# 🔹 หน้าสุ่มหวย (ต้องล็อกอินก่อน)
#@app.route("/", methods=["GET", "POST"])
#@login_required
#def lottery():
#    if request.method == "POST":
#        lottery_type = request.form["lottery_type"]
#       img_path = create_image(lottery_type)
#       return send_file(img_path, mimetype="image/png", as_attachment=True, download_name="lottery_result.png")
#    return render_template("index.html")
import zipfile  # เพิ่มการนำเข้า zipfile

@app.route("/", methods=["GET", "POST"])
@login_required
def lottery():
    if request.method == "POST":
        lottery_types = request.form.getlist("lottery_type")  # รับค่าหลายค่าจากตัวเลือกที่เลือก
        img_paths = []

        # สร้างภาพสำหรับแต่ละประเภทหวยที่เลือก
        for lottery_type in lottery_types:
            img_path = create_image(lottery_type)
            img_paths.append((lottery_type, img_path))  # เก็บประเภทหวยและ path ของไฟล์ภาพ

        # ถ้าต้องการให้ดาวน์โหลดทีละไฟล์
        if len(img_paths) == 1:
            return send_file(img_paths[0][1], mimetype="image/png", as_attachment=True, download_name="lottery_result.png")

        # หรือ ถ้าต้องการให้รวมหลายไฟล์ไว้ในไฟล์ zip
        zip_filename = "lottery_results.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for lottery_type, img_path in img_paths:
                # ตั้งชื่อไฟล์ใน zip ให้แตกต่างกัน เช่น ใช้ชื่อประเภทหวย
                zipf.write(img_path, os.path.basename(f"{lottery_type}.png"))

        return send_file(zip_filename, mimetype="application/zip", as_attachment=True, download_name=zip_filename)

    return render_template("index copy.html")

# 🔹 ฟังก์ชันสร้างรูปภาพ (เหมือนเดิม)
def create_image(lottery_type):
    bg_path = os.path.join("static", "Baan1.jpg")
    font_path = os.path.join("static", "Mali-Bold.ttf")

    image = Image.open(bg_path)
    draw = ImageDraw.Draw(image)

    font_large = ImageFont.truetype(font_path, 100)
    font_medium = ImageFont.truetype(font_path, 70)
    font_small = ImageFont.truetype(font_path, 40)

    #date_text = datetime.now().strftime("%d.%m.%y")
    #draw.text((250, 50), date_text, font=font_medium, fill="yellow")

    bbox = draw.textbbox((0, 0), lottery_type, font=font_medium)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # คำนวณตำแหน่งให้อยู่ตรงกลาง
    image_width = image.width
    x_position = (image_width - text_width) // 2  # ตำแหน่ง X ให้อยู่ตรงกลาง
    y_position = 50  # ให้ข้อความอยู่ด้านบน

    # วาดข้อความที่คำนวณแล้ว
    draw.text((x_position, y_position), lottery_type, font=font_medium, fill="white")

    #draw.text((250,50), lottery_type, font=font_medium, fill="white")

    num1, num2 = random.sample(range(0, 10), 2)

    # สร้างรายการเลขสองหลักที่ขึ้นต้นด้วย num1 และ num2
    all_tens = [f"{num1}{i}" for i in range(10)]
    all_units = [f"{num2}{i}" for i in range(10)]

    # สุ่มไม่ให้ซ้ำกัน
    tens = random.sample(all_tens, 1)
    tens2 = random.sample([x for x in all_tens if x not in tens], 1)
    tens3 = random.sample([x for x in all_tens if x not in tens + tens2], 1)

    units = random.sample(all_units, 1)
    units2 = random.sample([x for x in all_units if x not in units], 1)
    units3 = random.sample([x for x in all_units if x not in units + units2], 1)
    random_6_digits = "".join(random.choices(f"{num1}{num2}" + "0123456789", k=6))

    draw.text((595, 245), f"{num1} - {num2}", font=font_large, fill="white")
    draw.text((520, 450), " ".join(tens[:1]), font=font_large, fill="white")
    draw.text((520, 600), " ".join(tens2[:1]), font=font_large, fill="white")
    draw.text((520, 750), " ".join(tens3[:1]), font=font_large, fill="white")
    draw.text((770, 450), " ".join(units[:1]), font=font_large, fill="white")
    draw.text((770, 600), " ".join(units2[:1]), font=font_large, fill="white")
    draw.text((770, 750), " ".join(units3[:1]), font=font_large, fill="white")
    #draw.text((250, 520), f"วิน.{random_6_digits}", font=font_medium, fill="yellow")

    output_filename = f"output_{lottery_type}.png"
    output_path = os.path.join("static", output_filename)

    image.save(output_path)
    return output_path

if __name__ == "__main__":
    app.run(debug=True)