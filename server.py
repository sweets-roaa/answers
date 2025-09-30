# server.py (لرفع على Render أو أي VPS)
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))
# يمكن ربط مباراة محددة لاحقاً؛ هنا نحافظ على آخر حالة (بسيط)
answers = [-1] * NUM_QUESTIONS

@app.route("/save_ans", methods=["POST"])
def save_ans():
    global answers
    data = request.get_json(force=True)
    q_index = int(data.get("index", -1))
    ans = int(data.get("answer", -1))
    if 0 <= q_index < len(answers):
        answers[q_index] = ans
        return jsonify({"status": "ok", "answers": answers}), 200
    else:
        return jsonify({"status": "error", "msg": "invalid index"}), 400

@app.route("/get_ans", methods=["GET"])
def get_ans():
    return jsonify({"answers": answers})

@app.route("/reset", methods=["POST"])
def reset():
    global answers
    answers = [-1] * NUM_QUESTIONS
    return jsonify({"status": "reset", "answers": answers})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
