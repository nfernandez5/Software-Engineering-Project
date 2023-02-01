const getCookie = (name) => {
    if (document.cookie.length > 0) {
        let start = document.cookie.indexOf(name + "=");
        if (start != -1) {
            start = start + name.length + 1;
            let end = document.cookie.indexOf(";", start);
            if (end == -1) {
                end = document.cookie.length;
            }
            return unescape(document.cookie.substring(start, end));
        }
    }
    return "";
};

$.ajaxSetup({
    headers: { "X-CSRFToken": getCookie("csrftoken") }
});

const configureExistingFriendsCards = () => {
    const existingFriendsCards = document.querySelectorAll(".existing-friend-card");

    existingFriendsCards.forEach(card => {
        const clone = card.cloneNode(true);

        const friendshipID = clone.getAttribute("id").split("-")[1];

        clone.getElementsByClassName("remove-friend-btn")[0].addEventListener("click", () => {
            $.ajax({
                url: "http://127.0.0.1:8000/api/remove-friend",
                type: "post",
                data: {
                    friendshipID: friendshipID
                },
                success: (data) => {
                    populateExistingFriends(data);
                    configureExistingFriendsCards();
                },
                failure: (data) => {
                    console.log("Something went wrong");
                }
            });
        });

        card.parentElement.replaceChild(clone, card);
    });
};

const configurePendingFriendsCards = () => {
    const pendingFriendCards = document.querySelectorAll(".pending-friend-card");

    pendingFriendCards.forEach(card => {
        const clone = card.cloneNode(true);

        const requesterUserID = clone.getAttribute("id").split("-")[1];
        let friendRequestID = "";

        clone.classList.forEach(c => {
            if (c.includes("friendRequest"))
            {
                friendRequestID = c.split("-")[1];
            }
        });

        clone.getElementsByClassName("accept-friend-btn")[0].addEventListener("click", () => {
            $.ajax({
                url: "http://127.0.0.1:8000/api/accept-friend",
                type: "post",
                data: {
                    requesterUserID: requesterUserID,
                    friendRequestID: friendRequestID
                },
                success: (data) => {
                    populateExistingFriends(data.existingFriends);
                    populatePendingFriends(data.pendingFriends);
                    configureExistingFriendsCards();
                    configurePendingFriendsCards();
                },
                failure: (data) => {
                    console.log("Something went wrong");
                }
            });
        });

        clone.getElementsByClassName("decline-friend-btn")[0].addEventListener("click", () => {
            $.ajax({
                url: "http://127.0.0.1:8000/api/decline-friend",
                type: "post",
                data: {
                    requesterUserID: requesterUserID,
                    friendRequestID: friendRequestID
                },
                success: (data) => {
                    populateExistingFriends(data.existingFriends);
                    populatePendingFriends(data.pendingFriends);
                    configureExistingFriendsCards();
                    configurePendingFriendsCards();
                },
                failure: (data) => {
                    console.log("Something went wrong");
                }
            })
        });

        card.parentElement.replaceChild(clone, card);
    });
};

const populateExistingFriends = (friends) => {
    const existingFriendTemplate = document.querySelector("#existing-friend-template");
    const existingFriendsContainer = document.querySelector("#existing-friends-container");

    existingFriendsContainer.innerHTML = "";

    friends.forEach(friend => {
        const friendEntry = existingFriendTemplate.cloneNode(true);

        friendEntry.removeAttribute("id");
        friendEntry.setAttribute("id", `friendship-${friend.friendship_id}`);
        friendEntry.classList.add(`friend-${friend.friend_id}`);
        friendEntry.getElementsByClassName("name")[0].textContent = `${friend.first_name} ${friend.last_name}`;
        friendEntry.getElementsByClassName("university")[0].textContent = friend.university;
        friendEntry.getElementsByClassName("major")[0].textContent = friend.major;

        if (friend.profile_id == -1) // There is no profile for the friend
        {
            friendEntry.getElementsByClassName("view-friend-btn")[0].style.display = "None";
        }
        else
        {
            friendEntry.getElementsByClassName("view-friend-btn")[0].setAttribute("href", `http://127.0.0.1:8000/friend/profile?id=${friend.profile_id}`);
        }

        existingFriendsContainer.appendChild(friendEntry);
    });
};

const populatePendingFriends = (pendingFriends) => {
    const pendingFriendTemplate = document.querySelector("#pending-friend-template");
    const pendingFriendsContainer = document.querySelector("#pending-friends-container");

    pendingFriendsContainer.innerHTML = "";

    pendingFriends.forEach(pendingFriend => {
        const pendingFriendEntry = pendingFriendTemplate.cloneNode(true);

        pendingFriendEntry.removeAttribute("id");
        pendingFriendEntry.setAttribute("id", `pendingFriend-${pendingFriend.requester_id}`);
        pendingFriendEntry.classList.add(`friendRequest-${pendingFriend.request_id}`);
        pendingFriendEntry.getElementsByClassName("name")[0].textContent = `${pendingFriend.first_name} ${pendingFriend.last_name}`;
        pendingFriendEntry.getElementsByClassName("university")[0].textContent = pendingFriend.university;
        pendingFriendEntry.getElementsByClassName("major")[0].textContent = pendingFriend.major;

        pendingFriendsContainer.appendChild(pendingFriendEntry);
    });
}

const getPendingFriends = () => {
    $.ajax({
        url: "http://127.0.0.1:8000/api/get-pending-friends",
        type: "get",
        success: (data) => {
            populatePendingFriends(data);
            configurePendingFriendsCards();
            getFriends();
        },
        failure: (data) => {
            console.log("Something went wrong");
        }
    });
};

const getFriends = () => {
    $.ajax({
        url: "http://127.0.0.1:8000/api/get-friends",
        type: "get",
        success: (data) => {
            populateExistingFriends(data);
            configureExistingFriendsCards();
        },
        failure: (data) => {
            console.log("Something went wrong");
        }
    });
};

getPendingFriends();
getFriends();