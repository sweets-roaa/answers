import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))
answers = [-1] * NUM_QUESTIONS

@app.route("/save_ans", methods=["POST"])
def save_ans():
    global answers
    data = request.get_json(force=True)
    app.logger.info(f"Incoming save_ans payload: {data}")
    q_index = int(data.get("index", -1))
    ans = int(data.get("answer", -1))
    if 0 <= q_index < len(answers):
        answers[q_index] = ans
        app.logger.info(f"Updated answers => {answers}")
        return jsonify({"status": "ok", "answers": answers}), 200
    else:
        app.logger.warning(f"Invalid index {q_index} in payload")
        return jsonify({"status": "error", "msg": "invalid index"}), 400

@app.route("/get_ans", methods=["GET"])
def get_ans():
    """إرجاع آخر حالة للأجوبة"""
    return jsonify({"answers": answers})

@app.route("/reset", methods=["POST"])
def reset():
    """إعادة تعيين كل الأجوبة لقيمة -1"""
    global answers
    answers = [-1] * NUM_QUESTIONS
    app.logger.info("Answers reset")
    return jsonify({"status": "reset", "answers": answers})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
