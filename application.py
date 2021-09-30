from flask import Flask, render_template , request
from flask_socketio import SocketIO, send, emit
from threading import Lock
import time
from collections import defaultdict

app = Flask(__name__)
# configure socketIo
socketio = SocketIO(app)


strokes = defaultdict(list)
strokes_lock = Lock()



@app.route("/", methods = ['GET','POST'])
def chat():
    return render_template('chat.html')


# Whiteboard handling
@socketio.on('stroke-start')
def stroke_start(data):
    global strokes

    with strokes_lock:
        data['time'] = time.time()
        strokes[request.sid].append(data)


@socketio.on('stroke-update')
def stroke_update(data):
    global strokes

    with strokes_lock:
        stroke = strokes[request.sid][-1]
        stroke['points'].append(data)

        update_stroke = {'thickness': stroke['thickness'],
                         'color': stroke['color'],
                         'points': stroke['points'][-2:]}

    emit('draw-new-stroke', update_stroke, broadcast=True, include_self=False)


@socketio.on('stroke-delete')
def stroke_delete():
    global strokes

    with strokes_lock:
        strokes[request.sid].pop()

    emit('clear-board', broadcast=True)

@socketio.on('clear-board')
def clear_board():
    global strokes

    with strokes_lock:
        strokes.clear()
    emit('clear-board', broadcast=True, include_self=False)


@socketio.on('save-drawing')
def save_drawing(data):
    pass

if __name__ == "__main__":

    socketio.run(app, debug = True)