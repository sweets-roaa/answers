# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import threading

app = Flask(__name__)
CORS(app)

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))

answers = [-1] * NUM_QUESTIONS
update_id = 0
first_answer = True
reset_timer = None  # ⏱️ مؤقت لإعادة التصفير التلقائي


def schedule_reset(delay=4):
    """يعمل reset بعد delay ثواني"""
    global reset_timer

    # لو فيه مؤقت قديم، لغيه
    if reset_timer and reset_timer.is_alive():
        reset_timer.cancel()

    def do_reset():
        global answers, update_id, first_answer
        answers = [-1] * NUM_QUESTIONS
        update_id += 1
        first_answer = True
        print("✅ تم عمل reset تلقائي بعد اكتمال جميع الإجابات.")

    reset_timer = threading.Timer(delay, do_reset)
    reset_timer.start()


@app.route("/save_ans", methods=["POST"])
def save_ans():
    global answers, update_id, first_answer
    data = request.get_json(force=True)
    q_index = int(data.get("index", -1))
    ans = int(data.get("answer", -1))

    if 0 <= q_index < len(answers):
        # أول إجابة بالمحاولة
        if first_answer:
            answers = [-1] * NUM_QUESTIONS
            first_answer = False

        # خزّن الإجابة
        answers[q_index] = ans
        update_id += 1

        # 👇 إذا امتلأت جميع الخانات → جهّز reset بعد 4 ثواني
        if all(a != -1 for a in answers):
            schedule_reset(4)

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
    global answers, update_id, first_answer
    answers = [-1] * NUM_QUESTIONS
    update_id += 1
    first_answer = True
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
