
// Global Vars
let group_items_div = document.getElementById("group_items");

function getGroupItemDiv(id)
{
    return group_items_div.getElementsByClassName("item_"+id)[0];
}



function addItemToList(id)
{
    fetch("/addItemToList?id=" + id, { method: 'POST', body: id }).then(function(response) { return response.json(); }).then(
    function(item)
    {
        console.log(item);
        updateGroupItemDiv(item["name"], item["img_url"], id, item["quantity"]);
    }).catch(function() { console.log("Failed to add item " + id + " to group list"); });
}

function removeItemFromList(id)
{
    fetch("/removeItemFromList?id=" + id, { method: 'POST', body: id }).then(function(response) { return response.json(); }).then(
    function(item)
    {
        console.log(item);
        updateGroupItemDiv(item["name"], item["img_url"], id, item["quantity"]);
   }).catch(function() { console.log("Failed to remove item " + id + " to group list"); });
}


//
//  Adds an item div to the group's item if it doesn't exist.
//  if it does, simply update its quantity
function updateGroupItemDiv(name, picture, id, quantity=1)
{
    let item_div = getGroupItemDiv(id);
    if(item_div == null) // Item doesn't exist!!
    {
        if(quantity > 0)
        {
            let item_div = makeItemDiv(name, picture, id, quantity);
            item_div.onclick = function() { removeItemFromList(id) };
            group_items_div.appendChild(item_div);
        }
    }
    else
    {
        if(quantity == 0)
        {
            item_div.remove();
        }
        else
        {
            let item_quantity_div = item_div.getElementsByClassName("item_quantity")[0];
            item_quantity_div.innerHTML = quantity;
            if(quantity > 1)
            {
                item_quantity_div.setAttribute("style", "display: block;");
            }
            else
            {
                item_quantity_div.setAttribute("style", "display: none;");
            }
        }
    }
}

function makeItemDiv(name, picture, id, quantity=1)
{
    let item_div = document.createElement("div");
    item_div.classList.add("item", "item_"+id);

    let item_title_div = document.createElement("div");
    item_title_div.setAttribute("class", "item_title");
    item_title_div.innerHTML = name;
    item_div.appendChild(item_title_div);

    let item_quantity_div = document.createElement("div");
    item_quantity_div.setAttribute("class", "item_quantity");
    item_quantity_div.innerHTML = quantity;
    item_div.appendChild(item_quantity_div);
    item_quantity_div.setAttribute("style", "display: none;");

    if(quantity > 1)
    {
        item_quantity_div.setAttribute("style", "display: block;");
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
        for (idx in group_items)
        {
            item = group_items[idx];
            console.log(item);

            updateGroupItemDiv(item["name"], item["img_url"], item["id"], item["quantity"]);
        }
    }).catch(function() { console.log("Error when getting group items"); });
}

function fetchAddableItems()
{
    fetch("/addbleShoppingItems").then(function(response) { return response.json(); }).then(
    function(addable_items)
    {
        let addable_items_div = document.getElementById("addable_items")
        for (idx in addable_items)
        {
            item = addable_items[idx];

            let item_div = makeItemDiv(item["name"], item["img_url"], item["id"]);
            let id = item["id"]; // Stored variable to be passed in as var to func
            item_div.onclick = function() { addItemToList(id) };

            addable_items_div.appendChild(item_div);
        }
    }).catch(function() { console.log("Error when getting addable items."); });
}


fetchGroupItems();

fetchAddableItems();
