from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Digunakan untuk session dan flash messages

# Koneksi ke database MySQL
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password_mysql',
        database='makanan_db'
    )

# Halaman utama (sebelum login)
@app.route('/')
def index():
    return render_template('index.html')

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Username or Password is incorrect')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Halaman dashboard setelah login
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM foods')
    foods = cursor.fetchall()
    conn.close()
    
    return render_template('dashboard.html', foods=foods)

# Halaman tambah makanan
@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO foods (name, description, price) VALUES (%s, %s, %s)', (name, description, price))
        conn.commit()
        conn.close()
        
        flash('Food added successfully')
        return redirect(url_for('dashboard'))

    return render_template('add_food.html')

# Halaman edit makanan
@app.route('/edit_food/<int:id>', methods=['GET', 'POST'])
def edit_food(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM foods WHERE id = %s', (id,))
    food = cursor.fetchone()
    
    if not food:
        flash('Food not found')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        
        cursor.execute('UPDATE foods SET name = %s, description = %s, price = %s WHERE id = %s', 
                       (name, description, price, id))
        conn.commit()
        conn.close()
        
        flash('Food updated successfully')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_food.html', food=food)

# Hapus makanan
@app.route('/delete_food/<int:id>', methods=['GET'])
def delete_food(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM foods WHERE id = %s', (id,))
    conn.commit()
    conn.close()

    flash('Food deleted successfully')
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
