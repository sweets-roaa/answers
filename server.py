# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from threading import Timer

app = Flask(__name__)
CORS(app)

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))

answers = [-1] * NUM_QUESTIONS
update_id = 0
reset_timer = None  # ⏳ مؤقت لإعادة التعيين


# 🛠️ دالة تنفيذ reset
def do_reset():
    global answers, update_id
    answers = [-1] * NUM_QUESTIONS
    update_id += 1
    print("✅ Reset done automatically")


@app.route("/save_ans", methods=["POST"])
def save_ans():
    global answers, update_id, reset_timer
    data = request.get_json(force=True)
    q_index = int(data.get("index", -1))
    ans = int(data.get("answer", -1))

    if 0 <= q_index < len(answers):
        # 👇 إذا هاي أول إجابة جديدة → صفّر كل شيء
        if all(a == -1 for a in answers):
            answers = [-1] * NUM_QUESTIONS

        # سجل الإجابة
        answers[q_index] = ans
        update_id += 1

        # 🕒 تحضير reset:
        # - إذا امتلأت كل الخانات
        # - أو إذا آخر خانة وصلها جواب
        if all(a != -1 for a in answers) or (q_index == NUM_QUESTIONS - 1 and ans != -1):
            if reset_timer:
                reset_timer.cancel()
            reset_timer = Timer(4.0, do_reset)
            reset_timer.start()

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
    global answers, update_id, reset_timer
    answers = [-1] * NUM_QUESTIONS
    update_id += 1
    if reset_timer:
        reset_timer.cancel()
    return jsonify({
        "status": "reset",
        "answers": answers,
        "update_id": update_id,
        "timestamp": time.time()
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
