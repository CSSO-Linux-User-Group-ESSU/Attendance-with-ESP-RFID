

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("attendanceModal");
    const openModalBtn = document.getElementById("openModalBtn");
    const closeModalBtn = document.getElementById("closeModalBtn");

    // Open the modal
    openModalBtn.addEventListener("click", function() {
      modal.style.display = "flex";
    });

    closeModalBtn.addEventListener("click", function() {
      modal.style.display = "none";
    });

    window.addEventListener("click", function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }
    });
    const modal1 = document.getElementById("attendanceModal1");
    const openModalBtn1 = document.getElementById("openModalBtn1");
    const closeModalBtn1 = document.getElementById("closeModalBtn1");

    // Open the modal
    openModalBtn1.addEventListener("click", function() {
      modal1.style.display = "flex";
    });

    closeModalBtn1.addEventListener("click", function() {
      modal1.style.display = "none";
    });

    window.addEventListener("click", function(event) {
      if (event.target == modal1) {
        modal1.style.display = "none";
      }
    });
  });

