document.addEventListener("DOMContentLoaded", function () {

    /* ------------------------------------------------------------
       Auto-dismiss flash messages after a few seconds
       ------------------------------------------------------------ */
    var flashes = document.querySelectorAll(".flash");
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = "opacity 0.4s ease";
            flash.style.opacity = "0";
            setTimeout(function () {
                flash.remove();
            }, 400);
        }, 4000);
    });

    /* ------------------------------------------------------------
       Cover image preview in the "Add Book" modal
       ------------------------------------------------------------ */
    var coverInput = document.getElementById("cover_image");
    var previewWrap = document.getElementById("coverPreview");
    var previewImg = document.getElementById("coverPreviewImg");

    if (coverInput && previewWrap && previewImg) {
        coverInput.addEventListener("change", function () {
            var file = coverInput.files && coverInput.files[0];

            if (!file) {
                previewWrap.style.display = "none";
                previewImg.src = "";
                return;
            }

            var reader = new FileReader();
            reader.onload = function (event) {
                previewImg.src = event.target.result;
                previewWrap.style.display = "flex";
            };
            reader.readAsDataURL(file);
        });
    }

    /* ------------------------------------------------------------
       Confirm before submitting destructive forms
       (any <form data-confirm="...">)
       ------------------------------------------------------------ */
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            var message = form.getAttribute("data-confirm");
            if (!window.confirm(message)) {
                event.preventDefault();
            }
        });
    });

});