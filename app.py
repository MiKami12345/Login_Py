from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッションのセキュリティキー
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_login_app.db'
db = SQLAlchemy(app)

# ユーザーモデルを定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# ユーザーモデルにTODOリストを関連付ける
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)


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
            login_message = f"ログインに成功しました。"
            return render_template('login_success.html', login_message=login_message, username=user.username)
        else:
            # ログインに失敗した場合はlogin_error.htmlにリダイレクト
            return redirect(url_for('login_error'))

    return render_template('login.html')


# ログイン成功時のページ
@app.route('/login_success')
def login_success():
    if 'username' in session:
        # ログインユーザーのTODOリストを取得
        user = User.query.filter_by(username=session['username']).first()
        tasks = Task.query.filter_by(user_id=user.id).all()
        return render_template('login_success.html', tasks=tasks)
    else:
        return redirect(url_for('login'))


# ログインエラーページ
@app.route('/login_error')
def login_error():
    return render_template('login_error.html')


# ログアウト機能
@app.route('/logout', methods=['POST'])
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

# タスクの生成
@app.route('/create_task', methods=['POST'])
def create_task():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        description = request.form['task']  # 'task'フィールドから値を取得
        task = Task(user_id=user.id, description=description)
        db.session.add(task)
        db.session.commit()
        return jsonify({'message': 'タスクが作成されました'})  # JSON形式でメッセージを返す
    else:
        return jsonify({'message': 'ログインしていません'})  # ログインしていない場合もメッセージを返す

# タスクの削除
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        task = Task.query.filter_by(id=task_id, user_id=user.id).first()
        if task:
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'タスクが削除されました'})  # JSON形式でメッセージを返す
        else:
            return jsonify({'message': 'タスクが見つかりませんでした'})  # JSON形式でメッセージを返す
            
# ユーザーページのルートを追加
@app.route('/user_page')
def user_page():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        tasks = Task.query.filter_by(user_id=user.id).all()
        return render_template('user_page.html', username=username, tasks=tasks)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
