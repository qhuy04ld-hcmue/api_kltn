async function loadGraph(){
    try{
        const res = await fetch("/api/file/neo4j");
        //const res = await fetch("/neo4j/graph");
        if(!res.ok) throw new Error("API error");

        const data = await res.json();

        renderOverview(data);
        /*
        const nodes = new vis.DataSet(
            data.nodes.map(n => ({
                id: n.id,                     // internal id dùng cho graph
                label: n.label,
                color: getColor(n.label),
                properties: n.properties || {},
                businessId: n.properties?.id || null  // id thật của hệ thống
            }))
        );
            */
        const nodes = new vis.DataSet(
            data.nodes.map(n => ({
                id: n.id,
                label: n.label,
                color: getColor(n.label),
                title: n.title || null   // 👈 thêm dòng này
            }))
        );
        const edges = new vis.DataSet(
            data.edges.map(e => ({
                from: e.from,
                to: e.to,
                arrows: "to",
                label: e.label || ""
            }))
        );

        const network = new vis.Network(
            document.getElementById("graph"),
            { nodes, edges },
            { physics:true }
        );

        network.on("click", function(params){
            if(params.nodes.length > 0){
                const node = nodes.get(params.nodes[0]);
                showNodeDetail(node);
            }
        });

    }catch(err){
        console.error("Neo4j load error:", err);
    }
}


/* ===============================
   RESULTS OVERVIEW
================================ */
function renderOverview(data){

    const nodeStats = {};
    data.nodes.forEach(n=>{
        const label = n.label;
        nodeStats[label] = (nodeStats[label] || 0) + 1;
    });

    const relStats = {};
    data.edges.forEach(e=>{
        const type = e.label;
        relStats[type] = (relStats[type] || 0) + 1;
    });

    const container = document.getElementById("overview");

    container.innerHTML = `
        <h6>Nodes (${data.nodes.length})</h6>
        <div class="mb-3">
            ${renderBadges(nodeStats)}
        </div>

        <h6>Relationships (${data.edges.length})</h6>
        <div>
            ${renderBadges(relStats)}
        </div>
    `;
}


/* BADGE RENDER */
function renderBadges(stats){
    let html = "";

    Object.keys(stats)
        .sort((a,b)=>stats[b]-stats[a])
        .forEach(key=>{
            html += `
                <span style="
                    display:inline-block;
                    margin:4px;
                    padding:6px 12px;
                    border-radius:20px;
                    background:#eef2f7;
                    font-size:13px;
                    font-weight:600;
                ">
                    ${key} (${stats[key]})
                </span>
            `;
        });

    return html;
}


/* ===============================
   NODE DETAIL
================================ */
function showNodeDetail(node){
    const detail = document.getElementById("nodeDetail");

    let displayId = node.id;

    // Nếu có title thì parse nó
    if (node.title) {
        try {
            // title đang là string dạng "{'id': 'C10-TIN-T02-L08'}"
            const cleaned = node.title
                .replace(/'/g, '"');   // đổi single quote thành double quote

            const parsed = JSON.parse(cleaned);

            if (parsed.id) {
                displayId = parsed.id;
            }
        } catch (e) {
            console.log("Parse title error:", e);
        }
    }

    let html = `
        <h6 style="color:${node.color}">
            ${node.label}
        </h6>
        <hr>
        <div><strong>ID:</strong> ${displayId}</div>
        <hr>
    `;

    detail.innerHTML = html;
}


/* ===============================
   COLOR MAP
================================ */
function getColor(label){
    const colors = {
        Class:"#6ab04c",
        Subject:"#2980b9",
        Topic:"#e056fd",
        Lesson:"#f0932b",
        Thing:"#7f8c8d"
    };
    return colors[label] || "#bdc3c7";
}

loadGraph();



/*
async function loadGraph(){
    const res = await fetch("/neo4j/graph");
    const data = await res.json();

    const nodes = new vis.DataSet(
        data.nodes.map(n=>({
            id:n.id,
            label:n.label,
            color:getColor(n.type)
        }))
    );

    const edges = new vis.DataSet(data.edges);

    new vis.Network(
        document.getElementById("graph"),
        {nodes,edges},
        {physics:true}
    );
}

function getColor(type){
    const colors={
        Class:"#ff7675",
        Subject:"#74b9ff",
        Topic:"#55efc4",
        Lesson:"#ffeaa7"
    }
    return colors[type]||"#ccc";
}

loadGraph();
*/