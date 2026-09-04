const socket = io();

let participantRoomCode = "";
let hasVoted = false;


/* -----------------------------------------
   JOIN POLL
----------------------------------------- */

function joinPoll() {

    const roomInput =
        document.getElementById("roomInput");

    const roomCode =
        roomInput.value.trim().toUpperCase();

    if (roomCode.length !== 6) {

        showError(
            "Please enter a valid 6-character room code."
        );

        return;
    }

    participantRoomCode = roomCode;

    socket.emit("join_poll", {

        room_code: roomCode

    });

}


/* -----------------------------------------
   SUCCESSFULLY JOINED
----------------------------------------- */

socket.on("joined_poll", function(data) {

    hideElement("joinSection");

    document.getElementById(
        "waitingRoomCode"
    ).textContent = data.room_code;

    showElement("waitingSection");

    clearError();

    /*
       If the host has already started voting,
       immediately show the voting screen.
    */

    if (data.started) {

        showVotingScreen(
            data.question,
            data.options
        );

    }

});


/* -----------------------------------------
   POLL STARTED
----------------------------------------- */

socket.on("poll_started", function(data) {

    showVotingScreen(
        data.question,
        data.options
    );

});


/* -----------------------------------------
   SHOW VOTING SCREEN
----------------------------------------- */

function showVotingScreen(question, options) {

    hideElement("waitingSection");

    showElement("votingSection");

    document.getElementById(
        "questionText"
    ).textContent = question;

    const container =
        document.getElementById(
            "optionsContainer"
        );

    container.innerHTML = "";

    hasVoted = false;

    options.forEach(function(option, index) {

        const button =
            document.createElement("button");

        button.className = "option-btn";

        button.textContent = option;

        button.onclick = function() {

            submitVote(index);

        };

        container.appendChild(button);

    });

}


/* -----------------------------------------
   SUBMIT VOTE
----------------------------------------- */

function submitVote(optionIndex) {

    if (hasVoted) {

        return;

    }

    socket.emit("submit_vote", {

        room_code: participantRoomCode,

        option_index: optionIndex

    });

}


/* -----------------------------------------
   VOTE CONFIRMATION
----------------------------------------- */

socket.on("vote_submitted", function(data) {

    hasVoted = true;

    document.getElementById(
        "voteMessage"
    ).textContent = data.message;

    const buttons =
        document.querySelectorAll(
            ".option-btn"
        );

    buttons.forEach(function(button) {

        button.disabled = true;

    });

    showElement("resultsSection");

});


/* -----------------------------------------
   LIVE RESULTS
----------------------------------------- */

socket.on("results_updated", function(data) {

    showElement("resultsSection");

    displayParticipantResults(data);

});


/* -----------------------------------------
   FINAL RESULTS
----------------------------------------- */

socket.on("poll_ended", function(data) {

    displayParticipantResults(data);

    document.getElementById(
        "voteMessage"
    ).textContent =
        "The poll has ended. Final results are shown above.";

    const buttons =
        document.querySelectorAll(
            ".option-btn"
        );

    buttons.forEach(function(button) {

        button.disabled = true;

    });

});


/* -----------------------------------------
   DISPLAY RESULTS
----------------------------------------- */

function displayParticipantResults(data) {

    const container =
        document.getElementById(
            "participantResults"
        );

    if (!container) {

        return;

    }

    container.innerHTML = "";

    const totalVotes =
        data.total_votes || 0;

    data.options.forEach(function(option, index) {

        const votes =
            data.votes[index];

        let percentage = 0;

        if (totalVotes > 0) {

            percentage =
                (votes / totalVotes) * 100;

        }

        const resultItem =
            document.createElement("div");

        resultItem.className =
            "result-item";


        resultItem.innerHTML = `

            <div class="result-header">

                <span>
                    ${option}
                </span>

                <span>
                    ${votes} vote${votes === 1 ? "" : "s"}
                </span>

            </div>

            <div class="result-bar-container">

                <div
                    class="result-bar"
                    style="width: ${percentage}%">
                </div>

            </div>

            <small>
                ${percentage.toFixed(1)}%
            </small>

        `;

        container.appendChild(resultItem);

    });

}


/* -----------------------------------------
   ERROR MESSAGE
----------------------------------------- */

socket.on("error_message", function(data) {

    showError(data.message);

});


function showError(message) {

    const error =
        document.getElementById(
            "errorMessage"
        );

    if (error) {

        error.textContent = message;

    }

}


function clearError() {

    const error =
        document.getElementById(
            "errorMessage"
        );

    if (error) {

        error.textContent = "";

    }

}


/* -----------------------------------------
   HELPER FUNCTIONS
----------------------------------------- */

function hideElement(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.classList.add("hidden");

    }

}


function showElement(id) {

    const element =
        document.getElementById(id);

    if (element) {

        element.classList.remove("hidden");

    }

}