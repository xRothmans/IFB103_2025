from flask import Flask, render_template
from backend.analyse import analyse_bp

app = Flask(__name__)
app.register_blueprint(analyse_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="192.168.0.174", port=5000, debug=True)