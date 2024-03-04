// const { app, BrowserWindow, ipcMain } = require('electron');
// const path = require('path');

// const createWindow = () => {
//   const win = new BrowserWindow({
//     width: 800,
//     height: 600,
//     webPreferences: {
//       nodeIntegration: true
//     }
//   });

//   win.loadFile('login.html');
// };

// // Обработчик для регистрации пользователя
// ipcMain.on('register', (event, { username, password }) => {
//   // Добавляем пользователя в базу данных
//   db.run('INSERT INTO users (username, password) VALUES (?, ?)', [username, password], (error) => {
//     if (error) {
//       event.reply('registration-error', { error: 'Username already exists' });
//     } else {
//       event.reply('registration-success');
//     }
//   });
// });

// // Обработчик для входа пользователя
// ipcMain.on('login', (event, { username, password }) => {
//   // Проверяем пользователя в базе данных
//   db.get('SELECT * FROM users WHERE username = ? AND password = ?', [username, password], (error, row) => {
//     if (row) {
//       event.reply('login-success');
//     } else {
//       event.reply('login-error', { error: 'Invalid username or password' });
//     }
//   });
// });

// app.whenReady().then(() => {
//   createWindow();
// });

// app.on('window-all-closed', () => {
//   if (process.platform !== 'darwin') {
//     app.quit();
//   }
// });

// app.on('activate', () => {
//   if (BrowserWindow.getAllWindows().length === 0) {
//     createWindow();
//   }
// });



// const axios = require('axios');

// const sendMessage = async (message) => {
//   try {
//     const response = await axios.post('http://127.0.0.1:5000/api/send_message', {
//       message: message
//     });
//     console.log(response.data);
//   } catch (error) {
//     console.error(error);
//   }
// }

// // Пример использования
// sendMessage('Привет, это моё первое сообщение!');


const { app, BrowserWindow } = require('electron');
const axios = require('axios');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // mainWindow.loadFile('index.html');
  mainWindow.loadURL('http://127.0.0.1:5000/');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});

function sendMessage(message) {
  // console.log('Sending message:', message);
  axios.post('http://127.0.0.1:5000/api/send_message', {
    message: message
  })
  .then(response => {
    console.log('Server response:', response.data);
  })
  .catch(error => {
    console.error('Error sending message:', error);
  });
}

const { ipcMain } = require('electron');

ipcMain.on('message', (event, message) => {
  sendMessage(message);
});
