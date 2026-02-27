async function loadBuckets(){
    const res = await fetch("/minio/buckets");
    const data = await res.json();

    const div = document.getElementById("buckets");
    div.innerHTML="";

    data.forEach(b=>{
        div.innerHTML += `<p>${b}</p>`;
    });
}
