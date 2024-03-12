(function () {
    var fieldBlock = document.getElementById('field');
    var gameInfo = fieldBlock.dataset;
    var field = new TicTacField(gameInfo.size, gameInfo.min_length);
    var logBlock = document.getElementById('log');
  
    fieldBlock.innerHTML = field.render();
  
    const socket = new WebSocket('ws://' + window.location.hostname + ':8000' + window.location.pathname);
  
    socket.addEventListener('open', function (event) {
      console.log('WebSocket connection opened:', event);
    });
  
    socket.addEventListener('message', function (event) {
      var data = JSON.parse(event.data);
      switch (data.action) {
        case 'game-action':
          logBlock.innerHTML = '<p>' + data.details.message + '</p>' + logBlock.innerHTML;
          switch (data.details.type) {
            case 'move':
              field.setCellValue(data.details.x, data.details.y, data.details.val);
              break;
            case 'game-finish':
              field.highlightLine(data.details.win_line, '#18c155');
              logBlock.innerHTML = '<p>Game over!</p>' + logBlock.innerHTML;
              break;
            case 'game-aborted':
              logBlock.innerHTML = '<p>Player leave room!</p><p>Game over!</p>' + logBlock.innerHTML;
              break;
          }
          break;
        case 'warning':
          switch (data.details.type) {
            case 'spectator-connected':
              data.details.history.forEach(function (item, ind, arr) {
                field.setCellValue(item.x, item.y, ['X', 'O'][ind % 2]);
              });
              alert(data.details.message);
              break;
          }
      }
    });
  
    fieldBlock.addEventListener('click', function (e) {
      if (socket.readyState !== WebSocket.OPEN) { // Check if the socket is open
        return;
      }
      var target = e.target;
      if (target.dataset.content === 'cell') {
        var data = {
          x: target.dataset.x,
          y: target.dataset.y
        };
        socket.send(JSON.stringify({
            type: "move",
          details: data
        }));
      }
    });
  
  })();
  