for (var i = 1; i < product.length; i++) {
    document.getElementById("select1").innerHTML += `
    <option value="${i}">${product[i].title}</option>
    `;
    document.getElementById("select2").innerHTML += `
    <option value="${i}">${product[i].title}</option>
    `;
    document.getElementById("select3").innerHTML += `
    <option value="${i}">${product[i].title}</option>
    `;
    document.getElementById("select4").innerHTML += `
    <option value="${i}">${product[i].title}</option>
    `;
}

// Function for handling selection of item 1
function item1(a) {
    // Your logic for item 1
    document.getElementById("img1").src = product[a].image;
    document.getElementById("price1").innerHTML = "INR " + product[a].price;
    document.getElementById("desc1").innerHTML = product[a].description;
    document.getElementById("brand1").innerHTML = product[a].brand;
    document.getElementById("rating1").innerHTML = product[a].rating || "N/A";
    document.getElementById("specifications1").innerHTML = product[a].specifications || "N/A";
    document.getElementById("features1").innerHTML = product[a].features || "N/A";
}

function item2(a) {
    // Your logic for item 2
    document.getElementById("img2").src = product[a].image;
    document.getElementById("price2").innerHTML = "INR " + product[a].price;
    document.getElementById("desc2").innerHTML = product[a].description;
    document.getElementById("brand2").innerHTML = product[a].brand;
    document.getElementById("rating2").innerHTML = product[a].rating || "N/A";
    document.getElementById("specifications2").innerHTML = product[a].specifications || "N/A";
    document.getElementById("features2").innerHTML = product[a].features || "N/A";
}

function item3(a) {
    // Your logic for item 3
    document.getElementById("img3").src = product[a].image;
    document.getElementById("price3").innerHTML = "INR " + product[a].price;
    document.getElementById("desc3").innerHTML = product[a].description;
    document.getElementById("brand3").innerHTML = product[a].brand;
    document.getElementById("rating3").innerHTML = product[a].rating || "N/A";
    document.getElementById("specifications3").innerHTML = product[a].specifications || "N/A";
    document.getElementById("features3").innerHTML = product[a].features || "N/A";
}

function item4(a) {
    // Your logic for item 4
    document.getElementById("img4").src = product[a].image;
    document.getElementById("price4").innerHTML = "INR " + product[a].price;
    document.getElementById("desc4").innerHTML = product[a].description;
    document.getElementById("brand4").innerHTML = product[a].brand;
    document.getElementById("rating4").innerHTML = product[a].rating || "N/A";
    document.getElementById("specifications4").innerHTML = product[a].specifications || "N/A";
    document.getElementById("features4").innerHTML = product[a].features || "N/A";
}

function updateReportLink() {
    var select1 = document.getElementById("select1").value;
    var select2 = document.getElementById("select2").value;
    var select3 = document.getElementById("select3").value;
    var select4 = document.getElementById("select4").value;

    var filterParams = [];
    if (select1 != 0) filterParams.push("ProductID eq " + select1);
    if (select2 != 0) filterParams.push("ProductID eq " + select2);
    if (select3 != 0) filterParams.push("ProductID eq " + select3);
    if (select4 != 0) filterParams.push("ProductID eq " + select4);

    var filterString = filterParams.join(" or ");

    var powerBIReportUrl = "https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID&groupId=YOUR_GROUP_ID&$filter=" + encodeURIComponent(filterString);
    document.getElementById("powerbi-link").href = powerBIReportUrl;
}