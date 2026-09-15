---
name: CloudBase 开发指南
description: CloudBase 全栈开发指南（小程序 + Web + 后端）
---

# CloudBase 开发指南

## 快速开始 #

### 安装 CloudBase CLI

```bash
npm install -g @cloudbase/cli
```

### 登录

```bash
tcb login
```

### 创建小程序项目（集成 CloudBase）

```bash
tcb init
# 选择：小程序项目 + 云开发环境
```

---

## 小程序云开发 #

### 初始化云环境

```javascript
// app.js
App({
  onLaunch() {
    wx.cloud.init({
      env: 'your-env-id' // 云开发环境 ID
    });
  }
})
```

### 调用云函数

```javascript
// pages/index/index.js
Page({
  async addTodo() {
    const res = await wx.cloud.callFunction({
      name: 'addTodo',
      data: {
        title: '学习微信小程序',
        done: false
      }
    });
    console.log(res.result);
  }
})
```

### 操作云数据库

```javascript
// pages/index/index.js
const db = wx.cloud.database();

// 插入数据
db.collection('todos').add({
  data: {
    title: '学习微信小程序',
    done: false
  },
  success: (res) => {
    console.log(res._id);
  }
})

// 查询数据
db.collection('todos').where({
  done: false
}).get({
  success: (res) => {
    console.log(res.data);
  }
})

// 更新数据
db.collection('todos').doc('todo-id').update({
  data: {
    done: true
  }
})

// 删除数据
db.collection('todos').doc('todo-id').remove()
```

### 上传文件到云存储

```javascript
// pages/index/index.js
wx.cloud.uploadFile({
  cloudPath: 'example.png', // 云存储路径
  filePath: '/local/path/example.png', // 本地文件路径
  success: (res) => {
    console.log(res.fileID); // 云文件 ID
  }
})

// 下载云文件
wx.cloud.downloadFile({
  fileID: 'cloud://example.png', // 云文件 ID
  success: (res) => {
    console.log(res.tempFilePath); // 临时文件路径
  }
})
```

### 用户登录（天然免登录，获取 OPENID）

```javascript
// cloudfunctions/addTodo/index.js
const cloud = require('wx-server-sdk');
cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
});

exports.main = async (event, context) => {
  const { OPENID, APPID } = cloud.getWXContext(); // 获取 OPENID
  const db = cloud.database();
  
  await db.collection('todos').add({
    data: {
      ...event,
      _openid: OPENID,
      createTime: db.serverDate()
    }
  });
  
  return { success: true };
}
```

---

## Web 开发 #

### 安装 Web SDK

```bash
# npm / pnpm / yarn
npm install @cloudbase/js-sdk
```

### 初始化

```javascript
// src/main.js
import cloud from '@cloudbase/js-sdk';

const app = cloud.init({
  env: 'your-env-id' // 云开发环境 ID
});

export default app;
```

### 用户登录（需要配置登录方式）

```javascript
// src/main.js
import cloud from '@cloudbase/js-sdk';

const app = cloud.init({
  env: 'your-env-id'
});

// 匿名登录
app.auth().signInAnonymously().then((res) => {
  console.log('登录成功', res);
});

// 微信登录（需要在 CloudBase 控制台配置）
// 自定义登录（需要自己实现登录逻辑）
```

### 操作数据库

```javascript
// src/api/todo.js
import app from '@/main.js';

const db = app.database();

// 插入数据
db.collection('todos').add({
  title: '学习 CloudBase',
  done: false
}).then((res) => {
  console.log(res.id);
});

// 查询数据
db.collection('todos').where({
  done: false
}).get().then((res) => {
  console.log(res.data);
});

// 更新数据
db.collection('todos').doc('todo-id').update({
  done: true
}).then((res) => {
  console.log('更新成功');
});

// 删除数据
db.collection('todos').doc('todo-id').remove().then((res) => {
  console.log('删除成功');
});
```

---

## 云函数开发 #

### 创建云函数

```
cloudfunctions/
├── addTodo/
│   └── index.js
├── getTodos/
│   └── index.js
└── deleteTodo/
    └── index.js
```

### 编写云函数

```javascript
// cloudfunctions/addTodo/index.js
const cloud = require('wx-server-sdk');
cloud.init({
  env: cloud.DYNAMIC_CURRENT_ENV
});

exports.main = async (event, context) => {
  const { OPENID } = cloud.getWXContext();
  const db = cloud.database();
  
  await db.collection('todos').add({
    data: {
      ...event,
      _openid: OPENID,
      createTime: db.serverDate()
    }
  });
  
  return { success: true };
}
```

### 部署云函数

```bash
# 在微信开发者工具中：
# 右键 cloudfunctions/函数名 → 上传并部署

# 或使用 CloudBase CLI：
tcb fn deploy addTodo
```

---

## 静态网站托管 #

### 部署静态网站

```bash
# 构建前端项目
npm run build

# 部署到 CloudBase 静态托管
tcb hosting deploy ./dist -e your-env-id
```

### 访问静态网站

```
https://your-env-id.tcloudbaseapp.com
```

---

## 故障排查 #

| 问题 | 解决方案 |
|------|-----------|
| 云函数调用失败 | 检查云函数日志（CloudBase 控制台 → 云函数 → 日志） |
| 云数据库权限错误 | 检查安全规则（CloudBase 控制台 → 数据库 → 权限设置） |
| 静态网站部署失败 | 检查网络连接，或尝试使用 CloudBase CLI 部署 |
| 用户登录失败 | 检查是否在 CloudBase 控制台配置了登录方式 |
