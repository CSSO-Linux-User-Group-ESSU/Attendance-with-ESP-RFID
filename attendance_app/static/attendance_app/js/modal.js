

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
  });