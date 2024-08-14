for (const elmnt of document.querySelectorAll('.container-calendar-event')) {
    // dragElement(elmnt);
    [hour, minute] = elmnt.getAttribute('data-time-start').split(',');
    setEventTime(hour, minute, elmnt);    
    // dragElement(document.getElementById("drag-element-1"));
}
// dragElement(document.getElementById("drag-element-2"));

function setEventTime(hour, minute, elmnt) {
    position = (hour * 108) + (minute * 1.8);
    // const rect = elmnt.parentNode.getBoundingClientRect();
    // elment.children
    elmnt.setAttribute('data-scroll', position);
    elmnt.style.top = position + "px";
}

const modalLarge = document.querySelector('.modal-large');
const modalOverlay = document.querySelector('.modal-background-overlay');

function hideModalLarge() {
    modalLarge.classList.add('close');
    setTimeout(() => {
        modalLarge.style.removeProperty('visibility');
        modalLarge.classList.remove('close');
    }, 250);
    modalOverlay.style.opacity = '0%';
    setTimeout(() => {
        modalOverlay.style.removeProperty('opacity');
        modalOverlay.style.removeProperty('visibility');
    }, 500);
}
function showModalLarge() {
    if (modalOverlay.style.visibility == 'visible') {
        return;
    }
    modalOverlay.style.visibility = 'visible';
    modalOverlay.style.opacity = '100%';
    modalLarge.style.visibility = 'visible';
    modalLarge.classList.add('open');
    setTimeout(() => {
        modalLarge.classList.remove('open');
    }, 250)
}

// showModalLarge();
// setTimeout(() => {
//     hideModalLarge();
// }, 1000)

const cal = document.querySelector('.container-calendar');

function setCurrentTimePos(hour, minute, elmnt) {
    position = (hour * 108) + (minute * 1.8) + 5;
    const rect = elmnt.getBoundingClientRect();
    position -= (rect.height - 2) / 2
    elmnt.setAttribute('data-scroll', position);
    elmnt.style.top = position + "px";
}
cal.scrollTop = 108 * new Date().getHours();
// console.log('cal scroll height', cal.scrollHeight)

let currentDate = new Date();

let dayIcon = document.querySelector('.modal-app-icon-day');
let dateIcon = document.querySelector('.modal-app-icon-date');
dayIcon.innerText = currentDate.toLocaleDateString('en-us', { weekday: 'short' });
dateIcon.innerText = currentDate.getDate();

function updateTime() {
    let currentTimeElmnt = document.querySelector('.container-calendar-current-time');
    let currentTime = new Date();
    currentTimeElmnt.children[0].innerText = `${currentTime.getHours()}:${currentTime.getMinutes().toString().padStart(2, '0')}`;
    // setEventTime(currentTime.getHours(), currentTime.getMinutes(), currentTimeElmnt);
    setCurrentTimePos(currentTime.getHours(), currentTime.getMinutes(), currentTimeElmnt);
}

updateTime()
// setInterval(updateTime, 1000);

// console.log('cal scroll top', cal.scrollTop)

// setEventTime(8, 20, document.getElementById('drag-element-1'));
// setEventTime(8, 20, document.getElementById('drag-element-2'));

function dragElement(elmnt) {
    // console.log(elmnt.offsetTop, 'topOffset')
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
        let round = Math.round(parseInt(prevValue) / (5 * 1.8));
        scroll_pos_set = round * (5 * 1.8);
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