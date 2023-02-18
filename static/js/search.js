const input = document.querySelector("input");
const search = document.getElementById("related");
input.addEventListener('input', (e) => {
    fetch(`/auto?name=${input.value}`)
        .then((value) => {
            return value.json();
        })
        .then((json) => {
            if (json.response.length == 0) {
                search.classList.add("hide");
            } else {
                search.classList.remove("hide");
            }
            search.innerHTML = "";
            json.response.forEach(element => {
                let c = document.createElement('li');
                let b = document.createElement('a');
                c.classList.add("relitem");
                b.innerText = `${element.name}(id:${element.id})`;
                b.href = `/result?pid=${element.id}`;
                c.appendChild(b);
                search.appendChild(c);
            });
        })
});