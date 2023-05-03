from flask import Flask, jsonify, render_template
import pymysql.cursors

app = Flask(__name__)

# membuat koneksi ke database
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='db_siswa',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data-siswa')
def data_siswa():
    return render_template('dataSiswa.html')

@app.route('/get_siswa')
def get_siswa():
    try:
        with conn.cursor() as cursor:
            # melakukan query ke database
            sql = "SELECT * FROM siswa"
            cursor.execute(sql)

            # mengambil hasil query dan memasukkannya ke dalam list
            result = cursor.fetchall()
            data = []
            for row in result:
                data.append(row)
            
            # mengembalikan data sebagai response JSON
            return jsonify(data)
    except:
        return "Terjadi kesalahan pada server"

if __name__ == '__main__':
    app.run(debug=True)
