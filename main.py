from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key'


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('main.html', title="2DYES")


@app.route('/about_us', methods=['GET', 'POST'])
def about_usf():
    return render_template('about_us.html', title="2DYES")


@app.route('/list_bot', methods=['GET', 'POST'])
def list_botf():
    return render_template('list_bot.html', title="2DYES")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
