document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("city");
    const suggestionBox = document.getElementById("suggestions");

    input.addEventListener("input", async function () {
        const query = input.value;
        if (query.length < 2) {
            suggestionBox.innerHTML = "";
            return;
        }

        const res = await fetch(`/autocomplete?q=${query}`);
        const cities = await res.json();

        suggestionBox.innerHTML = "";
        cities.forEach(city => {
            const option = document.createElement("div");
            option.className = "suggestion";
            option.textContent = `${city.name}, ${city.country}`;
            option.onclick = () => {
                input.value = city.name;
                suggestionBox.innerHTML = "";
            };
            suggestionBox.appendChild(option);
        });
    });
});
