// Modified on https://github.com/thmsbfft/electron-wrap

const { app, Menu, BrowserWindow, shell } = require("electron");
const express = require("express");
const fs = require("fs");
const url = require("url");
var path = require("path");
const exec = require("child_process").exec;

const mode = "build";
const winProgramData = "C:\\ProgramData\\Anaconda3\\envs\\koov";
const WINDOW_WIDTH = 1280;
const WINDOW_HEIGHT = 720;

const appPath = app.getAppPath();
const resourcesPath = process.resourcesPath;
const osType = process.platform;

let envPath;
let pathVar;

switch (osType) {
  case "win32":
    envPath = (mode === "build" ? resourcesPath : appPath) + "\\env-" + osType;
    pathVar = envPath + ";";
    pathVar += envPath + "\\Scripts;";
    pathVar += envPath + "\\Library\\bin;";
    break;
  case "linux":
  case "darwin":
    envPath = (mode === "build" ? resourcesPath : appPath) + "/env-" + osType;
    pathVar = envPath + "/bin:";
    break;
  default:
    console.log("Cannot identify OS!");
    return;
}

if (osType === "win32") {
  let linked = fs.existsSync(winProgramData);

  if (linked) {
    const stat = fs.lstatSync(winProgramData);
    if (!stat.isSymbolicLink()) return;

    const target = fs.readlinkSync(winProgramData);
    if (target !== envPath) {
      fs.rmdirSync(winProgramData);
      linked = false;
    }
  }

  if (!linked) {
    const parentDir = path.dirname(winProgramData);
    if (!fs.existsSync(parentDir)) {
      fs.mkdirSync(parentDir, { recursive: true });
    }

    fs.symlinkSync(envPath, winProgramData, "dir", err => {
      if (err) {
        console.log(err);
        return;
      }
    });
  }
}

process.env.PATH = pathVar + process.env.PATH;

var w;
var app_ready = false;
var server_ready = false;
const server = express();
const port = 3000;

exec(
  "jupyter notebook --NotebookApp.token=test-secret --NotebookApp.allow_origin='*' --no-browser",
  (error, stdout, stderr) => {
    if (error) console.log(error);
    console.log(stdout);
  }
);

server.use(express.static(__dirname));
server.listen(port, function() {
  server_ready = true;
  if (app_ready) open();
});

function open() {
  let bw_options = {
    width: WINDOW_WIDTH,
    height: WINDOW_HEIGHT,
    resizable: true
  };

  w = new BrowserWindow(bw_options);

  w.setResizable(false);

  w.loadURL(
    url.format({
      pathname: "localhost" + ":" + port,
      protocol: "http:",
      slashes: true
    })
  );

  // w.webContents.openDevTools()

  w.on("closed", function() {
    w = null;
  });
}

app.on("ready", function() {
  app_ready = true;
  create_menus();
  if (server_ready) open();
});

app.on("window-all-closed", function() {
  app.quit();
});

function create_menus() {
  const template = [
    {
      label: app.getName(),
      submenu: [
        {
          role: "quit"
        }
      ]
    },
    {
      label: "Edit",
      submenu: [
        { role: "undo" },
        { role: "redo" },
        { type: "separator" },
        { role: "cut" },
        { role: "copy" },
        { role: "paste" },
        { role: "pasteandmatchstyle" },
        { role: "delete" },
        { role: "selectall" }
      ]
    },
    {
      label: "View",
      submenu: [
        {
          label: "Open in Browser...",
          click() {
            require("electron").shell.openExternal("http://localhost:" + port);
          }
        },
        {
          type: "separator"
        },
        { role: "reload" },
        { role: "forcereload" },
        { role: "toggledevtools" },
        { type: "separator" },
        { role: "resetzoom" },
        { role: "zoomin" },
        { role: "zoomout" },
        { type: "separator" },
        { role: "togglefullscreen" }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}
