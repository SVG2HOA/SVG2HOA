function toggleDropdown(menuId) {
    const dropdownMenu = document
    .getElementById(menuId);
    dropdownMenu.classList.toggle('hidden');
}

// Burger menus
document.addEventListener('DOMContentLoaded', function() {
    // open
    const burger = document.querySelectorAll('.navbar-burger');
    const menu = document.querySelectorAll('.navbar-menu');

    if (burger.length && menu.length) {
        for (var i = 0; i < burger.length; i++) {
            burger[i].addEventListener('click', function() {
                for (var j = 0; j < menu.length; j++) {
                    menu[j].classList.toggle('hidden');
                }
            });
        }
    }

    // close
    const close = document.querySelectorAll('.navbar-close');
    const backdrop = document.querySelectorAll('.navbar-backdrop');

    if (close.length) {
        for (var i = 0; i < close.length; i++) {
            close[i].addEventListener('click', function() {
                for (var j = 0; j < menu.length; j++) {
                    menu[j].classList.toggle('hidden');
                }
            });
        }
    }

    if (backdrop.length) {
        for (var i = 0; i < backdrop.length; i++) {
            backdrop[i].addEventListener('click', function() {
                for (var j = 0; j < menu.length; j++) {
                    menu[j].classList.toggle('hidden');
                }
            });
        }
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const startTimeInput = document.getElementById("reservation_time_start");
    const endTimeInput = document.getElementById("reservation_time_end");

    startTimeInput.addEventListener("change", function() {
        const startTime = new Date(`1970-01-01T${startTimeInput.value}:00`);
        const endTime = new Date(`1970-01-01T${endTimeInput.value}:00`);

        if (endTime <= startTime) {
            alert("End time must be after start time.");
            endTimeInput.value = '';
        }
    });
});

