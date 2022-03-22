

function addItemToList(id)
{
    fetch("/addItemToList?id=" + id, { method: 'POST', body: id }).then(function(item) {
        console.log(item)
        let group_items_div = document.getElementById("group_items");

        // If Item exists, just incrament quantity. Otherwise, Add new item to group item list div
        group_items_div.appendChild(makeItemDiv(item["name"], name["img_url"]));
   }).catch(function() { console.log("Failed to add item " + id + " to group list"); });
}

function removeItemFromList(id)
{
    fetch("/removeItemFromList?id=" + id, { method: 'POST', body: id }).then(function(item) {
        console.log(item)
        let group_items_div = document.getElementById("group_items");

        // If returned item's quantity is zero, just remove the item all togehter. Otherwise, update its quantity count.
   }).catch(function() { console.log("Failed to add item " + id + " to group list"); });
}

function makeItemDiv(name, picture, quantity=1)
{
    let item_div = document.createElement("div");
    item_div.setAttribute("class", "item");

    let item_title_div = document.createElement("div");
    item_title_div.setAttribute("class", "item_title");
    item_title_div.innerHTML = name;
    item_div.appendChild(item_title_div);

    if(quantity > 1)
    {
        let item_quantity_div = document.createElement("div");
        item_quantity_div.setAttribute("class", "item_quantity");
        item_quantity_div.innerHTML = quantity;
        item_div.appendChild(item_quantity_div);
    }

    let item_image = new Image();
    item_image.src = picture;
    item_image.setAttribute("class", "item_image");
    item_image.setAttribute("alt", name);
    item_image.setAttribute("title", name);
    item_div.appendChild(item_image);


    return item_div;
}

function fetchGroupItems()
{
    fetch("/groupsShoppingItems").then(function(response) { return response.json(); }).then(
    function(group_items)
    {
        let group_items_div = document.getElementById("group_items")
        for (idx in group_items)
        {
            item = group_items[idx];
            console.log(item);

            let item_div = makeItemDiv(item["name"], item["img_url"], item["quantity"]);
            item_div.onclick = function() { addItemToList(item["id"]) };

            group_items_div.appendChild(item_div);
        }
    }).catch(function() { console.log("Error when getting group items"); });
}

fetchGroupItems();

function fetchAddableItems()
{
    fetch("/addbleShoppingItems").then(function(response) { return response.json(); }).then(
    function(addable_items)
    {
        let addable_items_div = document.getElementById("addable_items")
        for (idx in addable_items)
        {
            item = addable_items[idx];

            let item_div = makeItemDiv(item["name"], item["img_url"]);
            let id = item["id"]; // Stored variable to be passed in as var to func
            item_div.onclick = function() { addItemToList(id) };

            addable_items_div.appendChild(item_div);
        }
    }).catch(function() { console.log("Error when getting addable items."); });
}


fetchAddableItems();
