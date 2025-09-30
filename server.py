# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time

app = Flask(__name__)
CORS(app)

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))

answers = [-1] * NUM_QUESTIONS
update_id = 0  # 🔑 رقم إصدار للتحديثات


@app.route("/save_ans", methods=["POST"])
def save_ans():
    global answers, update_id
    data = request.get_json(force=True)
    q_index = int(data.get("index", -1))
    ans = int(data.get("answer", -1))

    if 0 <= q_index < len(answers):
        # 👇 تحقق: هل أول إجابة بتنضاف (يعني كلهم -1)؟
        if all(a == -1 for a in answers):
            # صفر كل الإجابات أول مرة
            answers = [-1] * NUM_QUESTIONS

        # سجل الإجابة الجديدة
        answers[q_index] = ans
        update_id += 1  # 🔥 كل تعديل يزيد رقم التحديث
        return jsonify({
            "status": "ok",
            "answers": answers,
            "update_id": update_id,
            "timestamp": time.time()
        }), 200
    else:
        return jsonify({"status": "error", "msg": "invalid index"}), 400


@app.route("/get_ans", methods=["GET"])
def get_ans():
    return jsonify({
        "answers": answers,
        "update_id": update_id,
        "timestamp": time.time()
    })


@app.route("/reset", methods=["POST"])
def reset():
    global answers, update_id
    answers = [-1] * NUM_QUESTIONS
    update_id += 1  # كل عملية reset تعتبر تحديث جديد
    return jsonify({
        "status": "reset",
        "answers": answers,
        "update_id": update_id,
        "timestamp": time.time()
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ok", "msg": "server running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
