from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキーを設定します
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_login_app.db'
db = SQLAlchemy(app)

# ユーザーモデルを定義します
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# アプリケーションコンテキストを設定
with app.app_context():
    # データベースを初期化
    db.create_all()

# ログイン機能
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = user.username
            # ログインに成功した場合はlogin_success.htmlにリダイレクト
            return redirect(url_for('login_success'))
        else:
            # ログインに失敗した場合はlogin_error.htmlにリダイレクト
            return redirect(url_for('login_error'))

    return render_template('login.html')

# ログイン成功時のページ
@app.route('/login_success')
def login_success():
    if 'username' in session:
        return render_template('login_success.html')
    else:
        return redirect(url_for('login'))

# ログインエラーページ
@app.route('/login_error')
def login_error():
    return render_template('login_error.html')


# ログアウト機能
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# 新規登録機能
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # ユーザー名がすでに存在する場合はエラーメッセージを表示
            return render_template('registration_error.html')

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # 新規登録成功後に別のHTMLファイルにリダイレクト
        return redirect(url_for('registration_success'))

    return render_template('register.html')


# 新規登録成功ページ
@app.route('/registration_success')
def registration_success():
    return render_template('registration_success.html')



if __name__ == '__main__':
    app.run(debug=True)
