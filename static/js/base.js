console.log("home.js loaded");
document.addEventListener("DOMContentLoaded", () => {

    const flashes = document.querySelectorAll(".flash");

    flashes.forEach((flash) => {

        setTimeout(() => {

            flash.style.opacity = "0";

            setTimeout(() => {

                flash.remove();

            }, 500);

        }, 3000);

    });

});