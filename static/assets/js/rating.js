// Rating system

const stars = document.querySelectorAll('.star');
let selectedRating = 0;

stars.forEach((star, index) => {

    // Hover -> Highlight
    star.addEventListener('mouseover', () => {
        highlightStars(index);
    });

    // Mouse Out -> Reset to selected rating
    star.addEventListener('mouseout', () => {
        clearHighlight();
    });

    // Click -> Set Rating
    star.addEventListener('click', () => {
        selectedRating = index + 1;

        // Save selected stars visually
        stars.forEach((s, i) => {
            s.classList.toggle('selected', i < selectedRating);
        });

        document.getElementById("show-rating").textContent =
            "You selected: " + selectedRating + " Star";
    });
});

// Highlight on hover
function highlightStars(index) {
    stars.forEach((star, i) => {
        star.classList.toggle('highlighted', i <= index);
    });
}

// Remove hover highlight, show only selected stars
function clearHighlight() {
    stars.forEach((star, i) => {
        star.classList.toggle('highlighted', i < selectedRating);
    });
}
