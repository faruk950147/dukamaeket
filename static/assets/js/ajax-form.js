document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".color-btn");
    const priceBox = document.getElementById("product-price");

    buttons.forEach(btn => {
        btn.addEventListener("click", function () {

            const colorID = this.dataset.colorId;

            // Active button update
            buttons.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            // AJAX Request
            fetch("", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"
                },
                body: JSON.stringify({
                    "color_id": colorID,
                    "product_id": "{{ product.id }}"
                })
            })
            .then(res => res.json())
            .then(data => {
                priceBox.innerText = data.new_price;
            });

        });
    });

});
