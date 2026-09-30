const imageInput = document.getElementById("imageInput");

const dropArea = document.getElementById("dropArea");

const imagePreview = document.getElementById("imagePreview");

const previewContainer =
    document.getElementById("previewContainer");


// ==========================
// File Selection
// ==========================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (file) {

        showPreview(file);

    }

});


// ==========================
// Show Image Preview
// ==========================

function showPreview(file) {

    if (!file.type.startsWith("image/")) {

        alert("Please select an image file.");

        return;
    }


    const reader = new FileReader();


    reader.onload = function (event) {

        imagePreview.src = event.target.result;

        previewContainer.style.display = "block";

    };


    reader.readAsDataURL(file);
}


// ==========================
// Drag Over
// ==========================

dropArea.addEventListener("dragover", function (event) {

    event.preventDefault();

    dropArea.classList.add("dragover");

});


// ==========================
// Drag Leave
// ==========================

dropArea.addEventListener("dragleave", function () {

    dropArea.classList.remove("dragover");

});


// ==========================
// Drop
// ==========================

dropArea.addEventListener("drop", function (event) {

    event.preventDefault();

    dropArea.classList.remove("dragover");


    const file = event.dataTransfer.files[0];


    if (file) {

        imageInput.files = event.dataTransfer.files;

        showPreview(file);

    }

});












document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("recognitionForm");

    const button = document.getElementById("predictButton");

    const loadingContainer =
        document.getElementById("loadingContainer");


    if (!form || !button || !loadingContainer) {
        return;
    }


    form.addEventListener("submit", function () {

        /* Show loading animation */

        loadingContainer.style.display = "block";


        /* Change button text */

        button.innerHTML = "Analyzing...";


        /* Disable button */

        button.disabled = true;

        button.classList.add("loading");

    });

});