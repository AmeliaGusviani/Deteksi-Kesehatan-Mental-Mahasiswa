from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

app = Flask(__name__)

# === FUNGSI FUZZY PER VARIABEL INPUT ===
def fuzzy_stres_akademik(value):
    if value == 1:
        return {'rendah': 1.0, 'tinggi': 0.0}
    elif value == 2:
        return {'rendah': 0.7, 'tinggi': 0.3}
    elif value == 3:
        return {'rendah': 0.3, 'tinggi': 0.7}
    else:
        return {'rendah': 0.0, 'tinggi': 1.0}

def fuzzy_istirahat(value):
    if value == 1:
        return {'cukup': 1.0, 'kurang': 0.0}
    elif value == 2:
        return {'cukup': 0.6, 'kurang': 0.4}
    elif value == 3:
        return {'cukup': 0.3, 'kurang': 0.7}
    else:
        return {'cukup': 0.0, 'kurang': 1.0}

def fuzzy_motivasi(value):
    if value == 1:
        return {'tinggi': 1.0, 'rendah': 0.0}
    elif value == 2:
        return {'tinggi': 0.6, 'rendah': 0.4}
    elif value == 3:
        return {'tinggi': 0.3, 'rendah': 0.7}
    else:
        return {'tinggi': 0.0, 'rendah': 1.0}

def fuzzy_sosial(value):
    if value == 1:
        return {'baik': 1.0, 'buruk': 0.0}
    elif value == 2:
        return {'baik': 0.6, 'buruk': 0.4}
    elif value == 3:
        return {'baik': 0.3, 'buruk': 0.7}
    else:
        return {'baik': 0.0, 'buruk': 1.0}

def fuzzy_emosi(value):
    if value == 1:
        return {'stabil': 1.0, 'tidak_stabil': 0.0}
    elif value == 2:
        return {'stabil': 0.6, 'tidak_stabil': 0.4}
    elif value == 3:
        return {'stabil': 0.3, 'tidak_stabil': 0.7}
    else:
        return {'stabil': 0.0, 'tidak_stabil': 1.0}

def fuzzy_energi(value):
    if value == 1:
        return {'tinggi': 1.0, 'rendah': 0.0}
    elif value == 2:
        return {'tinggi': 0.6, 'rendah': 0.4}
    elif value == 3:
        return {'tinggi': 0.3, 'rendah': 0.7}
    else:
        return {'tinggi': 0.0, 'rendah': 1.0}

def fuzzy_tekanan(value):
    if value == 1:
        return {'rendah': 1.0, 'tinggi': 0.0}
    elif value == 2:
        return {'rendah': 0.7, 'tinggi': 0.3}
    elif value == 3:
        return {'rendah': 0.3, 'tinggi': 0.7}
    else:
        return {'rendah': 0.0, 'tinggi': 1.0}

# === FUNGSI Z KATEGORI OUTPUT ===
def z_sangat_sehat(alpha):
    return 60 + alpha * 40

def z_cenderung_sehat(alpha):
    return 50 + alpha * 20

def z_cenderung_buruk(alpha):
    return 30 + alpha * 20

def z_risiko_tinggi(alpha):
    return 10 + alpha * 20

# === INFERENSI TSUKAMOTO ===
def inferensi(fuzzified_inputs):
    rules = []
    for i in range(128):
        kondisi = format(i, '07b')
        alpha_list = []

        for idx, bit in enumerate(kondisi):
            val = list(fuzzified_inputs[idx].values())
            keys = list(fuzzified_inputs[idx].keys())
            alpha_list.append(val[0] if bit == '0' else val[1])

        alpha = min(alpha_list)

        if i < 16:
            z = z_sangat_sehat(alpha)
        elif i < 48:
            z = z_cenderung_sehat(alpha)
        elif i < 96:
            z = z_cenderung_buruk(alpha)
        else:
            z = z_risiko_tinggi(alpha)

        rules.append((alpha, z))
    return rules

# === DEFUZZIFIKASI ===
def defuzzifikasi(rules):
    atas = sum(alpha * z for alpha, z in rules)
    bawah = sum(alpha for alpha, _ in rules)
    return atas / bawah if bawah != 0 else 0

# === KATEGORISASI SKOR ===
def kategorikan(nilai):
    if nilai >= 80:
        return "Kesehatan mental Anda tergolong sangat sehat. Anda menunjukkan keseimbangan emosi dan mental yang sangat baik."
    elif nilai >= 60:
        return "Kesehatan mental Anda cenderung sehat. Secara umum Anda berada dalam kondisi yang stabil, namun tetap perlu menjaga keseimbangan."
    elif nilai >= 40:
        return "Kesehatan mental Anda cenderung buruk. Mungkin ada tekanan atau stres yang mulai mempengaruhi kondisi Anda."
    else:
        return "Anda berada pada risiko tinggi terhadap gangguan kesehatan mental. Sangat disarankan untuk mencari bantuan profesional atau konseling."

# === FLASK ROUTES ===
@app.route('/index', methods=['GET', 'POST'])
def index():
    hasil = False
    skor = 0
    kategori = ''
    jawaban = []

    if request.method == 'POST':
        try:
            inputs = [int(request.form.get(f'q{i+1}')) for i in range(7)]

            fuzzy_inputs = [
                fuzzy_stres_akademik(inputs[0]),
                fuzzy_istirahat(inputs[1]),
                fuzzy_motivasi(inputs[2]),
                fuzzy_sosial(inputs[3]),
                fuzzy_emosi(inputs[4]),
                fuzzy_energi(inputs[5]),
                fuzzy_tekanan(inputs[6])
            ]

            rules = inferensi(fuzzy_inputs)
            skor = defuzzifikasi(rules)
            kategori = kategorikan(skor)
            hasil = True
            jawaban = inputs

        except Exception as e:
            print(f"Error saat proses POST: {e}")

    return render_template('index.html', hasil=hasil, skor=skor, kategori=kategori, jawaban=jawaban)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

def generate_rules():
    rules = []
    for i in range(128):
        b = format(i, '07b')
        rule = {
            'stres': 'Rendah' if b[0] == '0' else 'Tinggi',
            'istirahat': 'Cukup' if b[1] == '0' else 'Kurang',
            'motivasi': 'Tinggi' if b[2] == '0' else 'Rendah',
            'sosial': 'Baik' if b[3] == '0' else 'Buruk',
            'emosi': 'Stabil' if b[4] == '0' else 'Labil',
            'energi': 'Tinggi' if b[5] == '0' else 'Rendah',
            'tekanan': 'Rendah' if b[6] == '0' else 'Tinggi'
        }
        rules.append(rule)
    return rules

@app.route('/about')
def about():
    rules = generate_rules()
    return render_template('about.html', rules=rules)
if __name__ == '__main__':
    app.run(debug=True)