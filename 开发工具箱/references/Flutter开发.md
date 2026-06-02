---
name: Flutter开发
description: Flutter跨平台应用开发指南（UI/状态管理/导航/打包）
---

# 二级：Flutter开发

**适用场景**：用户需要开发Flutter跨平台应用（iOS/Android/Web/桌面）。

---

## 三级执行：Flutter 开发流程

### 环境安装

```bash
# 安装 Flutter SDK
# 从 https://flutter.dev/docs/get-started/install 下载

# 添加到 PATH（Windows PowerShell）
$env:PATH += ";C:\flutter\bin"

# 验证安装
flutter doctor

# 安装 Android Studio（用于Android开发）
# 安装 Visual Studio（用于Windows开发）
```

### 创建新项目

```bash
# 创建新Flutter项目
flutter create my_app

# 指定平台
flutter create --platforms android,ios,web my_app

# 运行项目
cd my_app
flutter run
```

---

## UI 开发

### Widget 树结构

```dart
// lib/main.dart
import 'package:flutter/material.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'My App',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home'),
      ),
      body: Center(
        child: Text(
          'Hello Flutter!',
          style: TextStyle(fontSize: 24),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: Icon(Icons.add),
      ),
    );
  }
}
```

### 常用 Widget

| Widget | 说明 | 示例 |
|--------|------|------|
| `Container` | 容器，可设置边距/背景 | `Container(padding: ...)` |
| `Row` / `Column` | 水平/垂直布局 | `Row(children: [...])` |
| `Stack` | 堆叠布局 | `Stack(children: [...])` |
| `ListView` | 列表 | `ListView.builder(...)` |
| `GridView` | 网格 | `GridView.count(...)` |
| `Text` | 文本 | `Text('Hello')` |
| `Image` | 图片 | `Image.network(url)` |
| `Icon` | 图标 | `Icon(Icons.add)` |
| `ElevatedButton` | 按钮 | `ElevatedButton(onPressed: ...)` |

---

## 状态管理

### 方法1：setState（简单状态）

```dart
class CounterPage extends StatefulWidget {
  @override
  _CounterPageState createState() => _CounterPageState();
}

class _CounterPageState extends State<CounterPage> {
  int _counter = 0;

  void _increment() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Text('Count: $_counter'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _increment,
        child: Icon(Icons.add),
      ),
    );
  }
}
```

### 方法2：Provider（推荐）

```bash
# 添加依赖
flutter pub add provider
```

```dart
// lib/providers/counter_provider.dart
import 'package:flutter/material.dart';

class CounterProvider extends ChangeNotifier {
  int _count = 0;
  int get count => _count;

  void increment() {
    _count++;
    notifyListeners();
  }
}

// lib/main.dart
void main() {
  runApp(
    ChangeNotifierProvider(
      create: (context) => CounterProvider(),
      child: MyApp(),
    ),
  );
}

// 使用
class CounterPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final counter = Provider.of<CounterProvider>(context);
    
    return Scaffold(
      body: Center(
        child: Text('Count: ${counter.count}'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: counter.increment,
        child: Icon(Icons.add),
      ),
    );
  }
}
```

### 方法3：Riverpod（现代化）

```bash
flutter pub add flutter_riverpod
```

```dart
// lib/providers/counter_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'counter_provider.g.dart';

@riverpod
class Counter extends _$Counter {
  @override
  int build() => 0;

  void increment() => state++;
}
```

---

## 导航

### 基本导航

```dart
// 推入新页面
Navigator.of(context).push(
  MaterialPageRoute(builder: (context) => DetailPage()),
);

// 返回
Navigator.of(context).pop();

// 替换页面
Navigator.of(context).pushReplacement(
  MaterialPageRoute(builder: (context) => HomePage()),
);
```

### 命名路由

```dart
// lib/main.dart
MaterialApp(
  routes: {
    '/': (context) => HomePage(),
    '/detail': (context) => DetailPage(),
    '/settings': (context) => SettingsPage(),
  },
);

// 导航
Navigator.of(context).pushNamed('/detail');
```

### 传递参数

```dart
// 方法1：构造函数
Navigator.of(context).push(
  MaterialPageRoute(
    builder: (context) => DetailPage(itemId: 123),
  ),
);

// 方法2：路由参数
Navigator.of(context).pushNamed(
  '/detail',
  arguments: {'itemId': 123},
);
```

---

## 网络请求

### 使用 http 包

```bash
flutter pub add http
```

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<List<Post>> fetchPosts() async {
  final response = await http.get(
    Uri.parse('https://jsonplaceholder.typicode.com/posts'),
  );

  if (response.statusCode == 200) {
    final List<dynamic> json = jsonDecode(response.body);
    return json.map((item) => Post.fromJson(item)).toList();
  } else {
    throw Exception('Failed to load posts');
  }
}
```

### 使用 Dio（推荐）

```bash
flutter pub add dio
```

```dart
import 'package:dio/dio.dart';

final dio = Dio();

Future<List<Post>> fetchPosts() async {
  try {
    final response = await dio.get(
      'https://jsonplaceholder.typicode.com/posts',
    );
    return (response.data as List)
        .map((item) => Post.fromJson(item))
        .toList();
  } on DioException catch (e) {
    throw Exception('Failed to load posts: ${e.message}');
  }
}
```

---

## 本地存储

### SharedPreferences（轻量键值对）

```bash
flutter pub add shared_preferences
```

```dart
import 'package:shared_preferences/shared_preferences.dart';

// 保存
final prefs = await SharedPreferences.getInstance();
await prefs.setInt('counter', 42);
await prefs.setString('username', 'Alice');

// 读取
final counter = prefs.getInt('counter') ?? 0;
final username = prefs.getString('username') ?? '';
```

### Sqflite（关系型数据库）

```bash
flutter pub add sqflite path
```

```dart
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

// 初始化数据库
Future<Database> initDb() async {
  final dbPath = await getDatabasesPath();
  final path = join(dbPath, 'app.db');
  
  return openDatabase(
    path,
    version: 1,
    onCreate: (db, version) {
      return db.execute(
        'CREATE TABLE posts(id INTEGER PRIMARY KEY, title TEXT, body TEXT)',
      );
    },
  );
}

// 插入
Future<void> insertPost(Post post) async {
  final db = await initDb();
  await db.insert('posts', post.toMap());
}

// 查询
Future<List<Post>> getPosts() async {
  final db = await initDb();
  final maps = await db.query('posts');
  return maps.map((map) => Post.fromMap(map)).toList();
}
```

---

## 打包发布

### Android 打包

```bash
# 1. 修改 android/app/build.gradle
#   defaultConfig { applicationId "com.example.myapp" }

# 2. 生成签名密钥
keytool -genkey -v -keystore ~/upload-keystore.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias upload

# 3. 配置签名
# 创建 android/key.properties：
#   storePassword=<password>
#   keyPassword=<password>
#   keyAlias=upload
#   storeFile=~/upload-keystore.jks

# 4. 构建 release APK
flutter build apk --release

# 5. 构建 App Bundle（推荐）
flutter build appbundle --release
```

### iOS 打包

```bash
# 1. 在 Xcode 中配置签名
# 2. 构建 release
flutter build ios --release

# 3. 在 Xcode 中归档并上传 App Store
```

---

## 常用包推荐

| 包名 | 用途 | 安装 |
|------|------|------|
| `provider` | 状态管理 | `flutter pub add provider` |
| `riverpod` | 状态管理（现代化） | `flutter pub add flutter_riverpod` |
| `http` | 网络请求 | `flutter pub add http` |
| `dio` | 网络请求（功能更强） | `flutter pub add dio` |
| `shared_preferences` | 本地存储（键值对） | `flutter pub add shared_preferences` |
| `sqflite` | 本地数据库 | `flutter pub add sqflite` |
| `image_picker` | 图片选择 | `flutter pub add image_picker` |
| `camera` | 相机 | `flutter pub add camera` |
| `url_launcher` | 打开外部链接 | `flutter pub add url_launcher` |
| `package_info_plus` | 获取应用信息 | `flutter pub add package_info_plus` |

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| `flutter doctor` 有错误 | 根据提示安装缺失的依赖 |
| 运行慢 | 使用 `--release` 模式运行 |
| 包安装失败 | 检查 `pubspec.yaml` 格式，运行 `flutter pub get` |
| iOS 构建失败 | 更新 CocoaPods：`pod repo update` |
| Android 构建失败 | 检查 Gradle 版本，更新 SDK |

---

## 注意事项

1. **热重载** — 开发时使用 `r` 键热重载，不要用热重启
2. **平台差异** — 某些包只支持特定平台，注意查看文档
3. **图片资源** — 需要在 `pubspec.yaml` 中声明 assets
4. **性能优化** — 使用 `const` Widget，避免不必要的重建
