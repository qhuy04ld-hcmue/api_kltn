async function loadClasses(){
    const res = await fetch("/postgres/classes");
    const data = await res.json();

    const body = document.getElementById("pgBody");
    body.innerHTML="";

    data.forEach(c=>{
        body.innerHTML += `<tr><td>${c.id}</td><td>${c.name}</td></tr>`;
    });
}
