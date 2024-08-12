for (const elmnt of document.querySelectorAll('.container-calendar-event')) {
    dragElement(elmnt);
    [hour, minute] = elmnt.getAttribute('data-time').split(',');
    setEventTime(hour, minute, elmnt);    
    // dragElement(document.getElementById("drag-element-1"));
}
// dragElement(document.getElementById("drag-element-2"));

function setEventTime(hour, minute, elmnt) {
    position = (hour * 105) + (minute * 1.75)
    elmnt.setAttribute('data-scroll', position);
    elmnt.style.top = position + "px";
}

let currentTimeElmnt = document.querySelector('.container-calendar-current-time');
let currentTime = new Date();
setEventTime(currentTime.getHours(), currentTime.getMinutes(), currentTimeElmnt);

// setEventTime(8, 20, document.getElementById('drag-element-1'));
// setEventTime(8, 20, document.getElementById('drag-element-2'));

function dragElement(elmnt) {
    console.log(elmnt.offsetTop, 'topOffset')
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById(elmnt.id + "header")) {
        // if present, the header is where you move the DIV from:
        document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
    } else {
        // otherwise, move the DIV from anywhere inside the DIV:
        elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;

        // var rect = elmnt.parentNode.getBoundingClientRect();
        // console.log(e.clientY + 10);
        // console.log(pos2);

        // console.log(elmnt.offsetTop)

        // console.log(pos2, pos4)
        // console.log(elmnt.offsetTop - pos2)
        // if (elmnt.offsetTop < 0) {
        //     return;
        // } 
        // set the element's new position:
        // console.log(elmnt.offsetTop - pos2)
        // console.log(e.clientY)
        // console.log(Math.round((elmnt.offsetTop - pos2) / 110));
        let prev = elmnt.getAttribute('data-scroll') ? elmnt.getAttribute('data-scroll') : 0;
        prev = parseInt(prev);
        prevValue = prev - pos2;
        // scroll_pos = elmnt.getAttribute('data-scroll');
        // scroll_pos_set = elmnt.offsetTop - pos2;
        // console.log(scroll_pos);

        if (elmnt.offsetTop - pos2 < 0) {
            return;
        }

        elmnt.setAttribute('data-scroll', prevValue);
        //  else if (elmnt.offsetTop - pos2 )
        // console.log(scroll_pos);
        let round = Math.round(parseInt(prevValue) / (5 * 1.75));
        scroll_pos_set = round * (5 * 1.75);
        if (scroll_pos_set >= 0) {
            elmnt.style.top = scroll_pos_set + "px";
        }
        // console.log(scroll_pos_set);
        // elmnt.style.top = (Math.round((elmnt.offsetTop - pos2) / 110) * 110) + "px";
        elmnt.setAttribute('data-scroll', prevValue);
        // elmnt.style.transform = 'translateY(' + (elmnt.offsetTop - pos2) + 'px)';
        // console.log('translateY(' + (elmnt.offsetTop - pos2) + 'px)');
        // elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}