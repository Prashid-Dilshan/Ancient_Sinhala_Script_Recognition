
// ==========================================================
// Image Preview
// ==========================================================

const imageInput =
    document.getElementById("imageInput");

const dropArea =
    document.getElementById("dropArea");

const imagePreview =
    document.getElementById("imagePreview");

const previewContainer =
    document.getElementById("previewContainer");


// Only run image preview code
// when these elements exist

if (
    imageInput &&
    dropArea &&
    imagePreview &&
    previewContainer
) {

    // ==========================
    // File Selection
    // ==========================

    imageInput.addEventListener(
        "change",
        function () {

            const file = this.files[0];

            if (file) {

                showPreview(file);

            }

        }
    );


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

            imagePreview.src =
                event.target.result;

            previewContainer.style.display =
                "block";

        };


        reader.readAsDataURL(file);

    }


    // ==========================
    // Drag Over
    // ==========================

    dropArea.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            dropArea.classList.add(
                "dragover"
            );

        }
    );


    // ==========================
    // Drag Leave
    // ==========================

    dropArea.addEventListener(
        "dragleave",
        function () {

            dropArea.classList.remove(
                "dragover"
            );

        }
    );


    // ==========================
    // Drop
    // ==========================

    dropArea.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            dropArea.classList.remove(
                "dragover"
            );


            const file =
                event.dataTransfer.files[0];


            if (file) {

                imageInput.files =
                    event.dataTransfer.files;

                showPreview(file);

            }

        }
    );

}



// ==========================================================
// Loading Animation
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const form =
            document.getElementById(
                "recognitionForm"
            );

        const button =
            document.getElementById(
                "predictButton"
            );

        const loadingContainer =
            document.getElementById(
                "loadingContainer"
            );


        // Only run when recognition page
        // elements exist

        if (
            !form ||
            !button ||
            !loadingContainer
        ) {

            return;

        }


        form.addEventListener(
            "submit",
            function () {

                // Show loading animation

                loadingContainer.style.display =
                    "block";


                // Change button text

                button.innerHTML =
                    "Analyzing...";


                // Disable button

                button.disabled = true;


                button.classList.add(
                    "loading"
                );

            }
        );

    }
);



// ==========================================================
// Delete Confirmation Modal
// ==========================================================

let deleteForm = null;



// ==========================================================
// Open Delete Modal
// ==========================================================

function openDeleteModal(button) {

    // Find the form belonging to
    // the clicked Delete button

    deleteForm =
        button.closest(".delete-form");


    const modal =
        document.getElementById(
            "deleteModal"
        );


    if (!modal) {

        return;

    }


    // Show modal

    modal.classList.add("show");

}



// ==========================================================
// Close Delete Modal
// ==========================================================

function closeDeleteModal() {

    const modal =
        document.getElementById(
            "deleteModal"
        );


    if (!modal) {

        return;

    }


    // Hide modal

    modal.classList.remove("show");


    // Clear selected form

    deleteForm = null;

}



// ==========================================================
// Delete Modal Events
// ==========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const confirmButton =
            document.getElementById(
                "confirmDeleteButton"
            );


        const modal =
            document.getElementById(
                "deleteModal"
            );


        // If modal doesn't exist,
        // do nothing

        if (
            !confirmButton ||
            !modal
        ) {

            return;

        }



        // ==================================================
        // Confirm Delete
        // ==================================================

        confirmButton.addEventListener(
            "click",
            function () {

                if (deleteForm) {

                    // Submit the actual
                    // POST form

                    deleteForm.submit();

                }

            }
        );



        // ==================================================
        // Close Modal When Clicking Outside
        // ==================================================

        modal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === modal
                ) {

                    closeDeleteModal();

                }

            }
        );



        // ==================================================
        // Close Modal With ESC
        // ==================================================

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape"
                ) {

                    closeDeleteModal();

                }

            }
        );

    }
);

