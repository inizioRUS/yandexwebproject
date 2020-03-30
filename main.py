from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html', title="2DYES")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
