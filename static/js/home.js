const modal = document.getElementById("addBookModal");

const openBtn = document.getElementById("openModal");

const closeBtn = document.getElementById("closeModal");


openBtn.onclick = () => {

    modal.style.display = "flex";

};


closeBtn.onclick = () => {

    modal.style.display = "none";

};


window.onclick = (event)=>{

    if(event.target===modal){

        modal.style.display="none";

    }

};