from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data-siswa')
def data_siswa():
    return render_template('dataSiswa.html')

@app.route("/siswa", methods=["POST"])
def siswa():
    kelasId = request.form["kelas_id"]
    conn = pymysql.connect(host="localhost", user="root", password="", database="db_siswa")
    cur = conn.cursor()
    cur.execute("SELECT siswa.id, siswa.nama, kelas.nama FROM siswa JOIN kelas ON siswa.kelas_id = kelas.id WHERE kelas_id = %s", kelasId)
    siswa = cur.fetchall()
    return render_template("siswa.html", siswa=siswa)

if __name__ == '__main__':
    app.run(debug=True)
