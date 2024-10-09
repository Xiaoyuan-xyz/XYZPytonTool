# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request

from encrypy import encrypt_text, decrypt_text

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    output_text = ""
    input_text = ""

    if request.method == "POST":
        input_text = request.form.get("input_text")
        output_text = request.form.get("output_text")
        action = request.form.get("action")

        if action == "encrypt":
            output_text = encrypt_text(input_text)
        elif action == "decrypt":
            try:
                input_text = decrypt_text(output_text)
            except ValueError as e:
                print(e)
                output_text = "输入了不合法的字符串\n" + output_text

    return render_template("index.html", output_text=output_text, input_text=input_text)


if __name__ == "__main__":
    app.run(debug=True)
