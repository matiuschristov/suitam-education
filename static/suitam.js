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

const modals = {
    user_details: document.querySelector('#modal-user-details'),
    event_details: document.querySelector('#modal-event-details')
}
const modalOverlay = document.querySelector('.modal-background-overlay');

function hideModalLarge(id) {
    ele = modals[id]
    if (id == 'open') {
        ele = document.querySelector('.modal-large.open');
        console.log(ele);
    }
    ele.classList.remove('open');
    ele.classList.add('close');
    setTimeout(() => {
        ele.style.removeProperty('visibility');
        ele.classList.remove('close');
    }, 250);
    modalOverlay.style.opacity = '0%';
    setTimeout(() => {
        modalOverlay.style.removeProperty('opacity');
        modalOverlay.style.removeProperty('visibility');
    }, 500);
}
function showModalLarge(id) {
    ele = modals[id]
    if (modalOverlay.style.visibility == 'visible') {
        return;
    }
    modalOverlay.style.visibility = 'visible';
    modalOverlay.style.opacity = '100%';
    ele.style.visibility = 'visible';
    ele.classList.add('open');
}

function updateClassColor(id, color) {
    return new Promise((resolve, reject) => {
        var http = new XMLHttpRequest();
        http.open('POST', '/api/class/color/', true);
        http.setRequestHeader('Content-type', 'application/json');
        http.onreadystatechange = function () {
            if (http.readyState == 4 && http.status == 200) {
                console.log(http);
                resolve()
            } else if (http.readyState == 4 && http.status != 200) {
                reject(http.status)
            }
        }
        http.send(JSON.stringify({
            'id': id,
            'color': color
        }));
    })
}

function select_color() {
    let color_wrapper = document.querySelector('.modal-event-color-select-wrapper');
    for (selected of color_wrapper.querySelectorAll('.selected')) {
        selected.classList.remove('selected');
    }
    let event_preview = document.querySelector('.modal-event-color-preview-event');
    event_preview.style.setProperty('--event-color', `var(--color-default-${this.getAttribute('data-color')})`)
    // modal-event-color-preview-event
    this.classList.add('selected');
}

function showEventDetails() {
    let data = JSON.parse(this.getAttribute('data-json'));
    select_color.call(document.querySelector(`.modal-event-color-select[data-color=${data.color}]`));
    document.querySelector('.modal-event-title').innerText = data.name;
    document.querySelector('.modal-event-teacher').innerText = data.teacher;
    document.querySelector('.modal-event-location').innerText = data.room;
    document.querySelector('#modal-event-details').setAttribute('data-json', this.getAttribute('data-json'));
    showModalLarge('event_details');
}

function saveEventDetails() {
    let selectedColor = document.querySelector('.modal-event-color-select.selected')
    let selectedColorName = selectedColor.getAttribute('data-color');
    let data = JSON.parse(document.querySelector('#modal-event-details').getAttribute('data-json'));
    data.color = selectedColorName;
    updateClassColor(data.id, selectedColorName);
    for (const event of document.querySelectorAll(`[data-class-id="${data.id}"]`)) {
        event.style.setProperty('--event-color', `var(--color-default-${selectedColorName})`)
        event.setAttribute('data-json', JSON.stringify(data));
    }
    hideModalLarge('open');
}

function showStatus(message,icon, color) {
    let status = document.querySelector('.container-status');
    let statusWrapper = document.querySelector('.container-status-wrapper');
    statusWrapper.style.visibility = 'visible'
    status.style.backgroundColor = `rgba(var(--color-default-${color}))`;
    status.classList.add('open');
    status.querySelector('.container-status-text').innerText = message;
    status.querySelector('.container-status-icon').setAttribute('data-icon', icon);
}
// function hideStatus() {
//     let status = document.querySelector('.container-status');
//     // let statusWrapper = document.querySelector('.container-status-wrapper');
//     status.classList.add('close');
//     setTimeout(() => {
//         status.classList.remove('open');
//         statusWrapper.style.visibility = 'hidden'
//     }, 1000);
// }
// setTimeout(() => {
//     hideStatus()
// }, 1000)

// USERNAME-PASSSWORD-INCORRECT
const urlParams = new URLSearchParams(window.location.search);
const myParam = urlParams.get('code');
// print(myParam)

switch (myParam) {
    case 'USERNAME-PASSSWORD-INCORRECT':
        showStatus('Incorrect username or password please try again', 'exclamationmark.octagon', 'red');
    case 'SESSION-EXPIRED':
        showStatus('Your session has expired please sign in again', 'exclamationmark.octagon', 'red');
    case 'AUTH-REQUIRED':
        showStatus('You must be logged in to visit that page', 'exclamationmark.octagon', 'red');
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
cal.scrollTop = (108 * (new Date().getHours()-1));
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
    setCurrentTimePos(currentTime.getHours(), currentTime.getMinutes(), currentTimeElmnt);
}


updateTime()
setInterval(updateTime, 1000);

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