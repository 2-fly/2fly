function CreateTags(tableObj, table_tag, tags)
{
    var thead = tableObj.createTHead();
    thead.id = "head_" + table_tag;
    var row = document.createElement("tr");
    row.bgColor = "#ACD6FF";
    for (var idx in tags)
    {
        var cell = document.createElement("th");
        cell.id = "th_" + tags[idx];
        cell.appendChild(document.createTextNode(tags[idx]));
        row.appendChild(cell);
    }
    thead.appendChild(row);
}

function CreateData(tableObj, table_tag, items)
{
    var tbody = tableObj.createTBody();
    tbody.id = "body_" + table_tag;
    for (var i in items)
    {
        var row = document.createElement("tr");
        row.id = "tr_" + table_tag + "_" + i;
        for (var j in items[i])
        {
            var cell = document.createElement("td");
            cell.id = "td_" + table_tag + "_" + i + "_" + j;
            cell.appendChild(document.createTextNode(items[i][j]));
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }
}

function deleteTBody(tableObj, table_tag)
{
    var tbs = tableObj.getElementsByTagName("tbody");
    if (tbs[0])
    {
        tableObj.removeChild(tbs[0]);
    }
}

function CreateTable(args)
{
    var table_tag = args["table_tag"];
    var tags = args["tags"];
    var items = args["items"];

    var tableObj = document.getElementById(table_tag);
    tableObj.deleteTHead();
    deleteTBody(tableObj, table_tag);
    CreateTags(tableObj, table_tag, tags);
    CreateData(tableObj, table_tag, items);
}
