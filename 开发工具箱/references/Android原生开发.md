---
name: Android原生开发
description: Android原生应用开发指南（Kotlin/Compose/Material3）
---

# 二级：Android原生开发

**适用场景**：用户需要开发Android原生应用，或使用Kotlin/Compose。

---

## 三级执行：Android 开发流程

### 环境安装

```bash
# 安装 Android Studio
# 从 https://developer.android.com/studio 下载

# 安装命令行工具（可选）
sdkmanager --install "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

### 创建新项目

```
1. 打开 Android Studio
2. New Project → Empty Compose Activity
3. 选择语言：Kotlin
4. 最小SDK：API 24 (Android 7.0)
```

---

## Kotlin 基础

### 变量与函数

```kotlin
// 变量
val name: String = "Alice"  // 不可变
var age: Int = 25          // 可变

// 类型推断
val city = "Shanghai"      // 自动推断为 String
val score = 95             // 自动推断为 Int

// 函数
fun greet(name: String): String {
    return "Hello, $name!"
}

// 简化函数
fun add(a: Int, b: Int) = a + b

// Lambda
val sum = { x: Int, y: Int -> x + y }
```

### 类与对象

```kotlin
// 数据类（自动生成 equals/hashCode/toString）
data class User(
    val id: Int,
    val name: String,
    val email: String
)

// 使用
val user = User(1, "Alice", "alice@example.com")
println(user.name)  // Alice

// 继承
open class Animal(val name: String)
class Dog(name: String) : Animal(name) {
    fun bark() = println("$name says Woof!")
}
```

### 空安全

```kotlin
// 非空类型
val name: String = "Alice"

// 可空类型
val nullableName: String? = null

// 安全调用
val length = nullableName?.length  // 如果是 null，返回 null

// Elvis 操作符
val length = nullableName?.length ?: 0  // 如果是 null，返回 0

// 强制非空（危险）
val length = nullableName!!.length  // 如果是 null，抛异常
```

---

## Compose UI

### 基本组件

```kotlin
@Composable
fun Greeting(name: String) {
    Text(
        text = "Hello, $name!",
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold
    )
}

@Composable
fun MyButton() {
    Button(
        onClick = { /* 点击处理 */ },
        colors = ButtonDefaults.buttonColors(
            containerColor = MaterialTheme.colorScheme.primary
        )
    ) {
        Text("Click Me")
    }
}

@Composable
fun MyTextField() {
    var text by remember { mutableStateOf("") }
    
    TextField(
        value = text,
        onValueChange = { text = it },
        label = { Text("Enter text") }
    )
}
```

### 布局

```kotlin
@Composable
fun MyScreen() {
    // 垂直布局
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Line 1")
        Text("Line 2")
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = {}) {
            Text("Button")
        }
    }
    
    // 水平布局
    // Row { ... }
    
    // 堆叠布局
    // Box { ... }
}
```

### Material 3 主题

```kotlin
@Composable
fun MyApp() {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Purple40,
            secondary = PurpleGrey40,
            tertiary = Pink40
        ),
        typography = Typography
    ) {
        // App content
        MyScreen()
    }
}
```

---

## 状态管理

### remember + mutableStateOf

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    
    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### ViewModel（推荐）

```kotlin
// 添加依赖：implementation "androidx.lifecycle:lifecycle-viewmodel-compose:2.8.0"

class CounterViewModel : ViewModel() {
    private val _count = mutableStateOf(0)
    val count: State<Int> = _count
    
    fun increment() {
        _count.value++
    }
}

@Composable
fun CounterScreen(
    viewModel: CounterViewModel = viewModel()
) {
    Column {
        Text("Count: ${viewModel.count.value}")
        Button(onClick = { viewModel.increment() }) {
            Text("Increment")
        }
    }
}
```

---

## 导航

### Compose Navigation

```kotlin
// 添加依赖：implementation "androidx.navigation:navigation-compose:2.7.0"

@Composable
fun MyApp() {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = {
                    navController.navigate("detail/123")
                }
            )
        }
        composable(
            "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId")
            DetailScreen(itemId = itemId)
        }
    }
}
```

---

## 网络请求

### 使用 Retrofit + Kotlinx Serialization

```kotlin
// 添加依赖
// implementation "com.squareup.retrofit2:retrofit:2.9.0"
// implementation "com.squareup.retrofit2:converter-kotlinx-serialization:2.9.0"

// API 接口
interface ApiService {
    @GET("posts")
    suspend fun getPosts(): List<Post>
    
    @POST("posts")
    suspend fun createPost(@Body post: Post): Post
}

// Retrofit 实例
val retrofit = Retrofit.Builder()
    .baseUrl("https://jsonplaceholder.typicode.com/")
    .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
    .build()

val apiService = retrofit.create(ApiService::class.java)

// 使用（在 ViewModel 中）
viewModelScope.launch {
    try {
        val posts = apiService.getPosts()
        // 更新 UI 状态
    } catch (e: Exception) {
        // 处理错误
    }
}
```

---

## 本地存储

### DataStore（推荐替代 SharedPreferences）

```kotlin
// 添加依赖：implementation "androidx.datastore:datastore-preferences:1.1.0"

// 创建 DataStore
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

// 读取
val usernameFlow: Flow<String> = context.dataStore.data.map { preferences ->
    preferences[stringPreferencesKey("username")] ?: ""
}

// 写入
suspend fun saveUsername(username: String) {
    context.dataStore.edit { preferences ->
        preferences[stringPreferencesKey("username")] = username
    }
}
```

### Room 数据库

```kotlin
// 添加依赖
// implementation "androidx.room:room-runtime:2.6.0"
// implementation "androidx.room:room-ktx:2.6.0"
// kapt "androidx.room:room-compiler:2.6.0"

// Entity
@Entity(tableName = "posts")
data class Post(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val title: String,
    val body: String
)

// DAO
@Dao
interface PostDao {
    @Query("SELECT * FROM posts")
    suspend fun getAll(): List<Post>
    
    @Insert
    suspend fun insert(post: Post)
    
    @Delete
    suspend fun delete(post: Post)
}

// Database
@Database(entities = [Post::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun postDao(): PostDao
}

// 使用
val db = Room.databaseBuilder(
    context,
    AppDatabase::class.java, "app-db"
).build()

val posts = db.postDao().getAll()
```

---

## 权限申请

```kotlin
// 添加依赖：implementation "com.google.accompanist:accompanist-permissions:0.34.0"

@Composable
fun RequestPermission() {
    val permissionState = rememberPermissionState(
        permission = Manifest.permission.CAMERA
    )
    
    when {
        permissionState.status.isGranted -> {
            Text("Camera permission granted")
        }
        permissionState.status.shouldShowRationale -> {
            Column {
                Text("We need camera permission to take photos")
                Button(onClick = { permissionState.launchPermissionRequest() }) {
                    Text("Request Permission")
                }
            }
        }
        else -> {
            Button(onClick = { permissionState.launchPermissionRequest() }) {
                Text("Request Permission")
            }
        }
    }
}
```

---

## 打包发布

```bash
# 1. 生成签名密钥
keytool -genkey -v -keystore my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key

# 2. 配置签名（app/build.gradle.kts）
android {
    signingConfigs {
        create("release") {
            storeFile = file("my-release-key.jks")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = "my-key"
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}

# 3. 构建 release APK
./gradlew assembleRelease

# 4. 构建 App Bundle（推荐）
./gradlew bundleRelease
```

---

## 常用库推荐

| 库名 | 用途 | 添加依赖 |
|------|------|---------|
| **Retrofit** | 网络请求 | `implementation "com.squareup.retrofit2:retrofit:2.9.0"` |
| **Coil** | 图片加载 | `implementation "io.coil-kt:coil-compose:2.6.0"` |
| **Room** | 本地数据库 | `implementation "androidx.room:room-runtime:2.6.0"` |
| **DataStore** | 本地存储 | `implementation "androidx.datastore:datastore-preferences:1.1.0"` |
| **Hilt** | 依赖注入 | `implementation "com.google.dagger:hilt-android:2.50"` |
| **Kotlinx Coroutines** | 协程 | `implementation "org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0"` |

---

## 故障排查

| 问题 | 解决方案 |
|------|-----------|
| 构建失败 | 检查 Gradle 版本，运行 `./gradlew clean` |
| 依赖冲突 | 使用 `./gradlew app:dependencies` 查看依赖树 |
| Compose 预览不显示 | 确保 `@Preview` 注解的函数不接受参数 |
| 内存泄漏 | 使用 LeakCanary：`debugImplementation "com.squareup.leakcanary:leakcanary-android:2.14"` |

---

## 注意事项

1. **协程作用域** — 使用 `viewModelScope` 或 `lifecycleScope`，避免在 `CoroutineScope()` 中启动
2. **状态提升** — 将状态提升到共同的父 Composable
3. **副作用** — 使用 `LaunchedEffect`、`DisposableEffect` 等处理副作用
4. **性能优化** — 使用 `remember`、`derivedStateOf` 避免不必要的重组
