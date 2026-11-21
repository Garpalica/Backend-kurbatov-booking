fetch('/db/api/rooms/')
    .then(response => response.json())
    .then(data => {

        const container = document.getElementById('rooms-container');

        container.innerHTML = '';

        data.rooms.forEach(room => {

            const roomDiv = document.createElement('div');
            roomDiv.className = 'room-card';

            const title = document.createElement('h3');
            title.textContent = room.name;

            const capacity = document.createElement('p');
            capacity.textContent = `Вместимость: ${room.capacity}`;

            roomDiv.appendChild(title);
            roomDiv.appendChild(capacity);

            container.appendChild(roomDiv);
        });
    })
    .catch(error => console.error("Ошибка:", error));