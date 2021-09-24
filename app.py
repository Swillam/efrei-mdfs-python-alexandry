import sqlite3
from os.path import join
from json import dumps

from flask import Flask, redirect, render_template, request, url_for,send_from_directory
from werkzeug.exceptions import abort

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?',
                        (book_id,)).fetchone()
    conn.close()
    if book is None:
        abort(404)
    return book

def edit_book(book):
    conn = get_db_connection()
    conn.execute('UPDATE books SET title=?, author=? WHERE id=?',
                    (book['title'], book['author'],book['id']))
    conn.commit()
    conn.close()

def create_book(book):
    conn = get_db_connection()
    conn.execute('INSERT INTO books (title, author) VALUES (?, ?)',
                    (book['title'], book['author']))
    conn.commit()
    conn.close()

def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id=?',
                    (book_id,))
    conn.commit()
    conn.close()

###
#
#   UI
#
###

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(join(app.root_path, 'static'),
                               'favicon.ico')

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/book/<int:book_id>')
def book(book_id):
    book = get_book(book_id)
    return render_template('book.html',book=book)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == 'POST':
        book = dict(request.form)
        print(request.args.get('book_id'))
        book['id'] = request.args.get('book_id')
        if not book['title'] or not book['author']:
            return dumps('Title and author is required!') 
        if book.get('id'): edit_book(book)
        else: create_book(book)
        return redirect(url_for('index'))
    book = {}
    book_id = request.args.get('book_id')
    if book_id: book = dict(get_book(book_id))
    return render_template('edit.html',book=book)

###
#
#       API 
#
###

@app.route('/api',methods=['GET','POST','DELETE','PUT'])
def api():
    if request.method == 'GET':
        book_id = request.args.get('book_id')
        if not book_id : book_id = request.form['book_id']
        book = dict(get_book(book_id))
        
        return dumps(book,indent=4,sort_keys=True) 

    if request.method == "PUT":
        book = request.form
        if not book: return dumps("failed"),404
        edit_book(book)
        return dumps('success')

    if request.method == 'POST':
        book = request.form
        if not book: return dumps("failed"),404
        create_book(book)
        return dumps('success')

    if request.method == "DELETE":
        book_id = request.args.get('book_id')
        if not book_id: return dumps("book_id not found"),404
        delete_book(book_id)
        return dumps('success')

if __name__ == '__main__':
    app.run(debug=True)