(() => {
    let buttons = document.querySelectorAll("button[data-add-portion]");
    let counter = document.querySelector(".yield-value");
    const baseValue = parseInt(counter.innerText);

    function updateAllIngredients(cnt, toAdd) {
        let infos = document.querySelectorAll('.product-counter');
        infos.forEach((element) => {
            let base_number = parseFloat(element.innerText);
            let number = base_number / baseValue;
            number = (number * (baseValue + toAdd)).toFixed(2);
            element.innerHTML = number
        })
    }

    buttons.forEach(element => element.addEventListener('click', () => {
        let toAdd = parseInt(element.getAttribute("data-add-portion"));
        let local_counter = (parseInt(counter.innerHTML) + toAdd);
        if (local_counter < 1) {
            local_counter = 1
            return
        }
        counter.innerText = local_counter.toString();
        updateAllIngredients(parseInt(counter.innerHTML), toAdd);
    }))
})()
