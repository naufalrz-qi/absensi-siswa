from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash,  generate_password_hash
from datetime import datetime

app = Flask(__name__)
#koneksi
app.secret_key = 'bebasapasaja'
app.config['MYSQL_HOST'] ='localhost'
app.config['MYSQL_USER'] ='root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] ='db_siswa'
mysql = MySQL(app)


@app.route("/login")
def index():
    if "username" in session:
        return redirect(url_for("absensi"))
    return render_template("login.html")
 
@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        #cek data username
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s',(username, ))
        akun = cursor.fetchone()
        if akun is None:
            flash('Login Gagal, Cek Username Anda','danger')
        elif not check_password_hash(akun[2], password):
            flash('Login gagal, Cek Password Anda', 'danger')
        else:
            session['loggedin'] = True
            session['username'] = akun[1]
            return redirect(url_for('userpage'))
    return render_template('login.html')

@app.route('/registrasi', methods=('GET','POST'))
def registrasi():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        #cek username atau email
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username=%s',(username, ))
        akun = cursor.fetchone()
        if akun is None:
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s)', (username, generate_password_hash(password)))
            mysql.connection.commit()
            flash('Registrasi Berhasil','success')
        else :
            flash('Username atau email sudah ada','danger')
    return render_template('registrasi.html')

#logout
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Halaman absensi
@app.route('/absensi')
def absensi():
    if 'loggedin' in session:
        return render_template('absensi.html')
    flash('Harap Login dulu','danger')
    return redirect(url_for('login'))

@app.route('/input_absen')
def input_absensi():
    if 'loggedin' in session:
        return render_template('input_absen.html')
    flash('Harap Login dulu','danger')
    return redirect(url_for('login'))

@app.route('/get_siswa/<kelas_id>')
def get_siswa(kelas_id):
   # Memilih data siswa berdasarkan kelas yang dipilih
   cursor = mysql.connection.cursor()
   cursor.execute("SELECT id, nama FROM siswa WHERE kelas_id = %s", kelas_id)
   data = cursor.fetchall()
   
   # Membuat tabel HTML dari data siswa yang dipilih
   html = ''
   for row in data:
      html += '<tr>'
      html += '<td>' + str(row[0]) + '</td>'
      html += '<td>' + row[1] + '</td>'
      html += '<td>' + kelas_id + '</td>'
      html += '</tr>'
   
   return html

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('userpage.html')
    return render_template('index.html')

@app.route('/dashboard')
def userpage():
    if 'loggedin' in session:
        return render_template('userpage.html')
    flash('Harap Login dulu','danger')
    return redirect(url_for('login'))
    

@app.route('/data-siswa')
def data_siswa():
    if 'loggedin' in session:
        return render_template('dataSiswa.html')
    flash('Harap Login dulu','danger')
    return redirect(url_for('login'))
    
# Ini untuk simpan inputan absensi terbaru
@app.route('/simpan_absensi', methods=['POST'])
def simpan_absensi():
    cursor = mysql.connection.cursor()
    data_absen = []
    for data, keterangan in request.form.items():
        siswa_id = int(data.split('_')[0])
        mapel_id = int(data.split('_')[1])
        date = datetime.now().strftime('%Y-%m-%d')
        # data_absen.append({
        #     'siswa_id':siswa_id,
        #     'mata_pelajaran_id':mapel_id,
        #     'tanggal':date,
        #     'keterangan':keterangan
        #     })
        
        # Membuat kursor untuk mengirim perintah ke database


        # Menjalankan query untuk mengambil data absensi berdasarkan kelas
        query = "SELECT siswa.nama, kelas.nama as kelas,mata_pelajaran.nama, guru.nama, absensi.keterangan, absensi.siswa_id FROM absensi JOIN siswa ON absensi.siswa_id = siswa.id JOIN kelas ON siswa.kelas_id = kelas.id JOIN mata_pelajaran ON absensi.mata_pelajaran_id = mata_pelajaran.id JOIN guru ON mata_pelajaran.id_guru = guru.id  WHERE absensi.tanggal = %s AND absensi.mata_pelajaran_id = %s"
        cursor.execute(query, (mapel_id,date))

        # Mengambil semua baris hasil query
        rows = cursor.fetchall()

        # Menutup kursor
        cursor.close()

        # Menyusun data absensi ke dalam bentuk array of dict
        absensi = []
        for row in rows:
            absensi.append({
                'nama': row[0],
                'kelas': row[1],
                'mata_pelajaran': row[2],
                'guru': row[3],
                'keterangan':row[4],
                'siswa_id':row[5],
            })
  
        if absensi is not None:
            return render_template('warning.html')
        else:
            query = "INSERT INTO absensi (siswa_id, tanggal, keterangan, mata_pelajaran_id) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (siswa_id, date, keterangan, mapel_id))
            mysql.connection.commit()
        
            cursor.close()
            return render_template('result.html')

# Ini untuk api siswa
@app.route("/siswa", methods=["POST"])
def siswa():
    kelasId = request.form["kelas_id"]
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT siswa.id, siswa.nama, kelas.nama FROM siswa JOIN kelas ON siswa.kelas_id = kelas.id WHERE kelas_id = %s", kelasId)
    siswa = cursor.fetchall()
    return render_template("siswa.html", siswa=siswa)


@app.route('/api/absensi/<kelas>&<tanggal>&<mapel>', methods=['GET'])
def get_absensi(kelas,tanggal,mapel):
	# Membuat kursor untuk mengirim perintah ke database
	cursor = mysql.connection.cursor()


	# Menjalankan query untuk mengambil data absensi berdasarkan kelas
	query = "SELECT siswa.nama, kelas.nama as kelas,mata_pelajaran.nama, guru.nama, absensi.keterangan, absensi.siswa_id FROM absensi JOIN siswa ON absensi.siswa_id = siswa.id JOIN kelas ON siswa.kelas_id = kelas.id JOIN mata_pelajaran ON absensi.mata_pelajaran_id = mata_pelajaran.id JOIN guru ON mata_pelajaran.id_guru = guru.id  WHERE siswa.kelas_id = %s  AND absensi.tanggal = %s AND absensi.mata_pelajaran_id = %s"
	cursor.execute(query, (kelas,tanggal,mapel,))

	# Mengambil semua baris hasil query
	rows = cursor.fetchall()

	# Menutup kursor
	cursor.close()

	# Menyusun data absensi ke dalam bentuk array of dict
	absensi = []
	for row in rows:
		absensi.append({
			'nama': row[0],
			'kelas': row[1],
			'mata_pelajaran': row[2],
			'guru': row[3],
			'keterangan': row[4],
            'siswa_id':row[5]
		})

	# Mengembalikan data absensi dalam format JSON
	return jsonify(absensi)

@app.route('/api/input_absensi/<kelas>&<mapel>', methods=['GET'])
def get_input_absensi(kelas,mapel):
	# Membuat kursor untuk mengirim perintah ke database
	cursor = mysql.connection.cursor()


	# Menjalankan query untuk mengambil data absensi berdasarkan kelas
	query = "SELECT siswa.nama, kelas.nama as kelas,mata_pelajaran.nama, guru.nama, siswa.id, mata_pelajaran.id FROM siswa JOIN kelas ON siswa.kelas_id = kelas.id JOIN mata_pelajaran ON kelas.id = mata_pelajaran.id_kelas JOIN guru ON mata_pelajaran.id_guru = guru.id  WHERE siswa.kelas_id = %s AND mata_pelajaran.id = %s"
	cursor.execute(query, (kelas,mapel,))

	# Mengambil semua baris hasil query
	rows = cursor.fetchall()

	# Menutup kursor
	cursor.close()

	# Menyusun data absensi ke dalam bentuk array of dict
	absensi = []
	for row in rows:
		absensi.append({
			'nama': row[0],
			'kelas': row[1],
			'mata_pelajaran': row[2],
			'guru': row[3],
            'siswa_id':row[4],
            'mata_pelajaran_id':row[5],
		})

	# Mengembalikan data absensi dalam format JSON
	return jsonify(absensi)

if __name__ == '__main__':
    app.run(debug=True)
