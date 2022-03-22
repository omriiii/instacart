




function fetch_addalbe_items()
{
    fetch("/addble_shopping_items").then(function(response) { return response.json(); }).then(
    function(addable_items)
    {
        let addable_items_div = document.getElementById("addable_items")
        for (idx in addable_items)
        {
            item = addable_items[idx];

            let item_div = document.createElement("div");
            item_div.innerHTML = item["name"];
            addable_items_div.appendChild(item_div);
        }
    }).catch(function() { console.log("Error!!"); });
}

fetch_addalbe_items();