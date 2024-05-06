// createworkout.html scripts

// creatworkout.html prepopulate date- and time input fields
document.addEventListener("DOMContentLoaded", function() {
    // createworkout.html - Prepopulate date input field with current date
    document.querySelector("#date").valueAsDate = new Date();

    // createworkout.html - Prepopulate time input field with current time
    let today = new Date().toISOString().substr(11, 5);
    document.querySelector("#start-time").value = today;

});


// editworkout.html scripts

// editworkout.html clicking suggestion fills input box
// *part of autocomplete list
// declared outside of "DOMContentLoaded" so function can be called from HTML...
function displayName(value) {
    exerciseInputElement = document.querySelector("#exercise");
    exerciseListElement = document.querySelector("#exercise-list");

    exerciseInputElement.value = value;
    exerciseListElement.innerHTML = "";
}

// editworkout.html autocomplete list
document.addEventListener("DOMContentLoaded", function() {
    // autocomplete suggestions for exercise input field
    const exerciseListElement = document.querySelector("#exercise-list");
    const exerciseInputElement = document.querySelector("#exercise");

    // filters for requested API data
    const parameters = "?language=2&is_main=False&ordering=name&limit=400";
    // empty list to store transformed data
    let exercises = [];


    // populate exercises list with API data
    function fetchExercises() {
        fetch(`https://wger.de/api/v2/exercise/${parameters}`)
            .then((response) => response.json())
            .then((data) => {
                exercises = data.results.map((x) => x.name);

                // commented out, so suggestions only show, when user starts typing
                // loadData(exercises, exerciseListElement);
            });
    }


    fetchExercises();


    // load list data into element's inner HTML
    function loadData(data, element) {
        if (data) {
            // clearing element allows for loading up-to-date data without appending
            element.innerHTML = "";
            let innerElement = "";

            // add first 5 data items to innerElement
            for (let i = 0; i < 5; i++) {
                // do not show "undefined"
                if (data[i] === undefined) {
                    continue;
                }
                innerElement += `<li>${data[i]}</li>`;
            }

            // // add all data items to innerElement
            // data.forEach((item) => {
            //     innerElement += `<li>${item}</li>`;
            // });

            element.innerHTML = innerElement;

            // TODO: enable users to click suggestions
            const listElements = document.querySelectorAll("#exercise-list li");
            listElements.forEach((element) => element.setAttribute("onclick", `displayName("${element.innerHTML}")`));
            console.log(`displayName(${element.innerHTML})`);

        }
    }

    // filter user input (searchText)
    function filterData(data, searchText) {
        return data.filter((x) => x.toLowerCase().includes(searchText.toLowerCase()));
    }


    // EventListener
    exerciseInputElement.addEventListener("input", function() {
        // clears autocomplete suggestions at every function call, cleaning previous output
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



