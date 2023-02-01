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

const searchInput = document.querySelector("#friend-search-input");
const searchCategorySelect = document.querySelector("#friend-search-category");

let searchCategory = "name";

const configureSearchResultCards = () => {
    const searchResultCards = document.querySelectorAll(".search-result-card");

    searchResultCards.forEach(card => {
        const clone = card.cloneNode(true);

        const searchResultID = clone.getAttribute("id").split("-")[1];

        clone.addEventListener("mouseover", () => {
            clone.getElementsByClassName("card-overlay")[0].style.display = "block";
        });

        clone.addEventListener("mouseleave", () => {
            clone.getElementsByClassName("card-overlay")[0].style.display = "none";
        });

        clone.getElementsByClassName("add-friend-btn")[0].addEventListener("click", () => {
            $.ajax({
                url: "http://127.0.0.1:8000/api/add-friend",
                type: "post",
                data: {
                    requestedUserID: searchResultID
                },
                success: (data) => {
                    console.log("Sent request");
                    searchInput.dispatchEvent(new Event("input")); // Get the "Request Pending" to appear after requesting
                },
                failure: (data) => {
                    console.log("Something went wrong");
                }
            });
        });

        card.parentElement.replaceChild(clone, card);
    });
};

const populateSearchResults = (results) => {
    const searchResultTemplate = document.querySelector("#search-result-template");
    const searchResultsContainer = document.querySelector("#search-results-container");

    if (results.length === 0 && searchInput.value === "") {
        document.querySelector("#nothing-searched-msg").style.display = "block";
    }
    else {
        document.querySelector("#nothing-searched-msg").style.display = "none";
    }

    if (results.length === 0 && searchInput.value.length > 0) {
        document.querySelector("#no-results-msg").style.display = "block";
    }
    else {
        document.querySelector("#no-results-msg").style.display = "none";
    }

    searchResultsContainer.innerHTML = "";

    results.forEach(result => {
        const resultEntry = searchResultTemplate.cloneNode(true);

        resultEntry.removeAttribute("id");
        resultEntry.setAttribute("id", `user-${result.id}`);
        resultEntry.getElementsByClassName("name")[0].textContent = `${result.first_name} ${result.last_name}`;
        resultEntry.getElementsByClassName("university")[0].textContent = result.university;
        resultEntry.getElementsByClassName("major")[0].textContent = result.major;

        if (result.request_pending) {
            resultEntry.getElementsByClassName("request-pending-btn")[0].style.display = "inline";
            resultEntry.getElementsByClassName("add-friend-btn")[0].style.display = "none";
        }
        else {
            resultEntry.getElementsByClassName("request-pending-btn")[0].style.display = "none";
            resultEntry.getElementsByClassName("add-friend-btn")[0].style.dispatchEvent = "inline";
        }

        searchResultsContainer.appendChild(resultEntry);
    });
};

searchCategorySelect.addEventListener("change", (e) => {
    searchCategory = e.target.value;
    searchInput.value = "";
    searchInput.dispatchEvent(new Event("input"));
});

searchInput.addEventListener("input",  (e) => {
    const searchText = e.target.value;
    if (searchText != "") {
        $.ajax({
            url: "http://127.0.0.1:8000/api/find-friends",
            type: "post",
            data: {
                category: searchCategory,
                text: searchText
            },
            success: (data) => {
                populateSearchResults(data);
                configureSearchResultCards();
            },
            failure: (data) => {
                console.log("Something went wrong");
            }
        });
    }
    else {
        populateSearchResults([]);
    }
});