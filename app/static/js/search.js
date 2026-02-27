async function searchData() {
    const q = document.getElementById("keyword").value;

    const res = await fetch(`/search/?q=${q}`);
    const data = await res.json();

    renderResult(data);
}

function renderResult(data){
    const div = document.getElementById("result");
    div.innerHTML = "";

    data.forEach(item=>{
        div.innerHTML += `
            <div class="card mb-2">
                <div class="card-body">
                    <h5>${item.title}</h5>
                    <p>${item.content}</p>
                </div>
            </div>
        `;
    });
}
