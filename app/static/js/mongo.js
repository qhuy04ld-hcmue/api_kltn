async function loadCollections(){
    const res = await fetch("/mongo/collections");
    const data = await res.json();

    const div = document.getElementById("collections");
    div.innerHTML="";

    data.forEach(c=>{
        div.innerHTML += `<p>${c}</p>`;
    });
}
