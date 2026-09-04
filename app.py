from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit
import random
import string

app = Flask(__name__)

app.config["SECRET_KEY"] = "live-polling-secret"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# --------------------------------------------------
# STORE ACTIVE POLLS
# --------------------------------------------------

polls = {}


# --------------------------------------------------
# GENERATE UNIQUE ROOM CODE
# --------------------------------------------------

def generate_room_code():

    while True:

        code = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        if code not in polls:
            return code


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# ADMIN PAGE
# --------------------------------------------------

@app.route("/admin")
def admin():

    return render_template("admin.html")


# --------------------------------------------------
# PARTICIPANT PAGE
# --------------------------------------------------

@app.route("/participant")
def participant():

    return render_template("participant.html")


# --------------------------------------------------
# RESULTS PAGE
# --------------------------------------------------

@app.route("/results")
def results():

    return render_template("results.html")


# ==================================================
# ADMIN - CREATE POLL
# ==================================================

@socketio.on("create_poll")
def create_poll(data):

    # Get question
    question = data.get("question", "").strip()

    # Get options
    options = data.get("options", [])

    # Make sure options is a list
    if not isinstance(options, list):

        emit(
            "error_message",
            {
                "message": "Invalid options."
            }
        )

        return

    # Remove empty options
    options = [
        str(option).strip()
        for option in options
        if str(option).strip()
    ]

    # Check question
    if not question:

        emit(
            "error_message",
            {
                "message": "Question cannot be empty."
            }
        )

        return

    # Check number of options
    if len(options) < 2 or len(options) > 6:

        emit(
            "error_message",
            {
                "message": "Poll must have between 2 and 6 options."
            }
        )

        return

    # Generate room code
    room_code = generate_room_code()

    # Store poll
    polls[room_code] = {

        "question": question,

        "options": options,

        "votes": [0] * len(options),

        "participants": set(),

        "started": False,

        "ended": False,

        "voters": set()

    }

    print()
    print("===================================")
    print("POLL CREATED")
    print("Room Code:", room_code)
    print("Question:", question)
    print("Options:", options)
    print("===================================")
    print()

    # Send information back to admin
    emit(
        "poll_created",
        {
            "room_code": room_code,
            "question": question,
            "options": options
        }
    )


# ==================================================
# PARTICIPANT - JOIN POLL
# ==================================================

@socketio.on("join_poll")
def join_poll(data):

    # Get room code
    room_code = data.get(
        "room_code",
        ""
    ).strip().upper()

    # Check room
    if room_code not in polls:

        emit(
            "error_message",
            {
                "message": "Room not found. Check the room code."
            }
        )

        return

    poll = polls[room_code]

    # Check if poll ended
    if poll["ended"]:

        emit(
            "error_message",
            {
                "message": "This poll has already ended."
            }
        )

        return

    # Add participant to Socket.IO room
    join_room(room_code)

    # Add participant socket ID
    poll["participants"].add(request.sid)

    participant_count = len(
        poll["participants"]
    )

    print(
        f"Participant joined {room_code}. "
        f"Total participants: {participant_count}"
    )

    # Send joining information
    emit(
        "joined_poll",
        {
            "room_code": room_code,

            "question": poll["question"],

            "options": poll["options"],

            "started": poll["started"]
        }
    )

    # Update participant count for everyone
    socketio.emit(
        "participant_count",
        {
            "count": participant_count
        },
        room=room_code
    )


# ==================================================
# ADMIN - START POLL
# ==================================================

@socketio.on("start_poll")
def start_poll(data):

    room_code = data.get(
        "room_code",
        ""
    ).strip().upper()

    # Check room
    if room_code not in polls:

        emit(
            "error_message",
            {
                "message": "Poll not found."
            }
        )

        return

    poll = polls[room_code]

    # Check if already ended
    if poll["ended"]:

        emit(
            "error_message",
            {
                "message": "This poll has already ended."
            }
        )

        return

    # Start voting
    poll["started"] = True

    print(
        f"Voting started for room {room_code}"
    )

    # Send to all connected users
    socketio.emit(
        "poll_started",
        {
            "question": poll["question"],

            "options": poll["options"]
        },
        room=room_code
    )


# ==================================================
# PARTICIPANT - SUBMIT VOTE
# ==================================================

@socketio.on("submit_vote")
def submit_vote(data):

    room_code = data.get(
        "room_code",
        ""
    ).strip().upper()

    option_index = data.get(
        "option_index"
    )

    # Check room
    if room_code not in polls:

        emit(
            "error_message",
            {
                "message": "Poll not found."
            }
        )

        return

    poll = polls[room_code]

    # Check whether voting has started
    if not poll["started"]:

        emit(
            "error_message",
            {
                "message": "Voting has not started yet."
            }
        )

        return

    # Check whether poll ended
    if poll["ended"]:

        emit(
            "error_message",
            {
                "message": "Voting has ended."
            }
        )

        return

    # Check whether participant joined this room
    if request.sid not in poll["participants"]:

        emit(
            "error_message",
            {
                "message": "You are not part of this poll."
            }
        )

        return

    # Prevent double voting
    if request.sid in poll["voters"]:

        emit(
            "error_message",
            {
                "message": "You have already voted."
            }
        )

        return

    # Validate option index
    if not isinstance(
        option_index,
        int
    ):

        emit(
            "error_message",
            {
                "message": "Invalid option."
            }
        )

        return

    if (
        option_index < 0
        or
        option_index >= len(
            poll["options"]
        )
    ):

        emit(
            "error_message",
            {
                "message": "Invalid option."
            }
        )

        return

    # Add voter
    poll["voters"].add(
        request.sid
    )

    # Increase vote
    poll["votes"][option_index] += 1

    selected_option = poll[
        "options"
    ][option_index]

    total_votes = sum(
        poll["votes"]
    )

    print()
    print("VOTE RECEIVED")
    print("Room:", room_code)
    print("Option:", selected_option)
    print("Total votes:", total_votes)
    print()

    # Confirm vote to participant
    emit(
        "vote_submitted",
        {
            "message": "Vote submitted successfully!"
        }
    )

    # Send updated results to everyone
    socketio.emit(
        "results_updated",
        {
            "options": poll["options"],

            "votes": poll["votes"],

            "total_votes": total_votes
        },
        room=room_code
    )


# ==================================================
# ADMIN - END POLL
# ==================================================

@socketio.on("end_poll")
def end_poll(data):

    room_code = data.get(
        "room_code",
        ""
    ).strip().upper()

    # Check room
    if room_code not in polls:

        emit(
            "error_message",
            {
                "message": "Poll not found."
            }
        )

        return

    poll = polls[room_code]

    # Check if already ended
    if poll["ended"]:

        emit(
            "error_message",
            {
                "message": "Poll has already ended."
            }
        )

        return

    # End poll
    poll["ended"] = True

    # Find highest vote count
    highest_votes = max(
        poll["votes"]
    )

    # Find winners
    winners = [
        index
        for index, votes
        in enumerate(poll["votes"])
        if votes == highest_votes
    ]

    # First winner is used if there is a tie
    winner_index = winners[0]

    total_votes = sum(
        poll["votes"]
    )

    print()
    print("===================================")
    print("POLL ENDED")
    print("Room:", room_code)
    print("Total votes:", total_votes)
    print("Winner:", poll["options"][winner_index])
    print("===================================")
    print()

    # Send final results
    socketio.emit(
        "poll_ended",
        {
            "question": poll["question"],

            "options": poll["options"],

            "votes": poll["votes"],

            "total_votes": total_votes,

            "winner_index": winner_index
        },
        room=room_code
    )


# ==================================================
# USER CONNECTED
# ==================================================

@socketio.on("connect")
def handle_connect():

    print(
        "User connected:",
        request.sid
    )


# ==================================================
# USER DISCONNECTED
# ==================================================

@socketio.on("disconnect")
def handle_disconnect():

    print(
        "User disconnected:",
        request.sid
    )

    # Remove user from participant lists
    for room_code, poll in polls.items():

        if request.sid in poll["participants"]:

            poll["participants"].remove(
                request.sid
            )

            participant_count = len(
                poll["participants"]
            )

            # Update remaining users
            socketio.emit(
                "participant_count",
                {
                    "count": participant_count
                },
                room=room_code
            )


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    print()
    print("===================================")
    print("     LIVE POLLING APPLICATION")
    print("===================================")
    print()

    print("Open in browser:")
    print("http://127.0.0.1:5000")

    print()

    print("Admin:")
    print("http://127.0.0.1:5000/admin")

    print()

    print("Participant:")
    print("http://127.0.0.1:5000/participant")

    print()
    print("===================================")

    socketio.run(
        app,
        debug=False,
        use_reloader=False,
        port=5000
    )
