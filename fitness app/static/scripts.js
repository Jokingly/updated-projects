// ---------------------------------------------------------------- editworkout.html - show/hide forms buttons ----------------------------------------------------------------

// editworkout.html
// show/hide forms with event listeners
document.addEventListener("DOMContentLoaded", function() {

    document.documentElement.addEventListener("click", (e) => {

        // visibility toggles for following edit fields:
        // - datetime
        // - note
        // - add set
        // - edit set
        // switch statement for readability
        switch(true) {
            // datetime edit fields
            case e.target.matches('.edit-datetime-button, .edit-datetime-button *'):
                document.getElementById('edit-datetime-fields').classList.toggle('hide');
                break;

            // note edit field
            case e.target.matches('.edit-note-button, edit-note-button *'):
                document.getElementById('note-form').classList.toggle('hide');
                break;

            // add set fields
            case e.target.matches('.add-set-button'):
                const targetElements = document.getElementsByClassName(e.target.value);

                for (let element of targetElements) {
                    element.classList.toggle('hide');                    
                }
                break;

            // edit set fields
            case e.target.matches('.edit-set-button, .edit-set-button *'):
                let targetElems = document.getElementsByClassName(e.target.value);
                
                if (e.target.value === undefined) {
                    targetElems = document.getElementsByClassName(e.target.parentNode.value);
                }

                for(let element of targetElems) {
                    element.classList.toggle('hide');
                }
                break;
        }
    });
});


// ---------------------------------------------------------------- editworkout.html - autofill suggestions ----------------------------------------------------------------
// editworkout.html - populate exercise input box with autosuggestion
// *part of autocomplete list
// declared outside of "DOMContentLoaded" so function can be called from HTML...
function displayName(value) {
    const exerciseInputElement = document.querySelector("#exercise");
    const exerciseListElement = document.querySelector("#exercise-list");

    exerciseInputElement.value = value;
    exerciseListElement.innerHTML = "";
}


// editworkout.html - exercise autocomplete suggestions
document.addEventListener("DOMContentLoaded", function() {

// ========================================================= WIP =========================================================
// REDESIGN TO PULL SUGGESTIONS FROM LOCAL fitnessapp.db
    // autocomplete suggestions for exercise input field
    const exerciseListElement = document.querySelector("#exercise-list");
    const exerciseInputElement = document.querySelector("#exercise");

    // filters for requested API data
    const parameters = "pull";
    // const parameters = "?language=2&is_main=False&ordering=name&limit=400";
    // empty list to store transformed data
    let exercises = [];


    // populate exercises list with API data
    function fetchExercises() {

        // fetch(`http://127.0.0.1:5000/exercise/${parameters}`)
        fetch(`http://127.0.0.1:5000/exercise`)
            .then((response) => response.json())
            .then((data) => {
                // return array of exercise names
                exercises = data.map((object) => object.name);
            });
    }

    fetchExercises();


    // load list data into element's inner HTML
    function loadData(data, element) {
        if (data) {
            // clearing element to load up-to-date data
            element.innerHTML = "";
            let innerElement = "";

            // add first 5 items to innerElement
            for (let i = 0; i < 5; i++) {
                // do not show "undefined"
                if (data[i] === undefined) {
                    continue;
                }
                innerElement += `<li>${data[i]}</li>`;
            }

            element.innerHTML = innerElement;

            // enable users to click suggestions
            const listElements = document.querySelectorAll("#exercise-list li");
            listElements.forEach((element) => element.setAttribute("onclick", `displayName("${element.innerHTML}")`));
        }
    }


    // filter user input (searchText)
    function filterData(data, searchText) {
        return data.filter((x) => x.toLowerCase().includes(searchText.toLowerCase()));
    }


    // EventListener
    exerciseInputElement.addEventListener("input", function() {
        // clears suggestions at every function call
        removeElements(exerciseListElement);

        // show autocomplete suggestions, when input box is not empty
        if (exerciseInputElement.value != "") {
            // store list of filtered data in variable
            const filteredData = filterData(exercises, exerciseInputElement.value);
            // pass filtered data back into loadData to update "autocomplete suggestions"
            loadData(filteredData, exerciseListElement);
        }
    });


    // clear list of autocomplete suggestions
    function removeElements(element) {
        element.innerHTML = "";
    }
});


// redundant, as using bootstrap collapse feature instead
// editworkout.html show/hide workout info (date, start time, end time) editing form

// document.addEventListener("DOMContentLoaded", function() {
//     const editWorkoutWorkoutInfo = document.querySelector("#editworkout-info");
//     const editWorkoutWorkoutInfoButton = document.querySelector("#editworkout-info button")
//     const editWorkoutWorkoutInfoForm = document.querySelector("#editworkout-form");
//     const editWorkoutWorkoutInfoFormButton = document.querySelectorAll("#editworkout-form button");

//     editWorkoutWorkoutInfoButton.addEventListener("click", function() {
//         editWorkoutWorkoutInfoForm.style.visibility = "visible";
//     });

//     editWorkoutWorkoutInfoFormButton.forEach( item => {
//         item.addEventListener("click", function() {
//             editWorkoutWorkoutInfoForm.style.visibility = "hidden";
//         });
//     });
// });



