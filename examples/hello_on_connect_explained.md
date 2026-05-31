# hello_on_connect 示例说明

文件：`examples/hello_on_connect_test.uya`

这个示例展示了用 `uya-uip` 实现一个最小功能：

> 当 TCP 连接建立后，发送 `helloworld`

---

## 1. 核心思想

在 `uya-uip` 里，不是像 BSD socket 一样直接：

```c
accept();
send(fd, "helloworld", 10, 0);
```

而是：

1. 协议栈处理输入包
2. 协议栈把连接状态反映到 `rt.flags`
3. 你的应用代码检查是否发生了“连接建立”事件
4. 若建立，则调用 `uip_send()` 挂载要发送的数据
5. 之后由底层主循环调用 `uip_arp_out()` 和网卡发送

---

## 2. 最小应用函数

示例里的核心函数是：

```uya
fn hello_on_connect(rt: &UipRuntime) void {
    if uip_connected(rt.flags) {
        const msg: [byte: 10] = ['h','e','l','l','o','w','o','r','l','d'];
        uip_send(rt, &msg[0], 10u16);
    }
}
```

含义：

- `uip_connected(rt.flags)`：当前事件是否表示连接刚建立
- `uip_send(...)`：告诉 uIP 本次要发送 10 字节数据

---

## 3. 运行时里发生了什么

调用 `uip_send(rt, &msg[0], 10u16)` 后，通常会更新：

- `rt.slen`
- `rt.sappdata`

也就是：
- 发送长度是多少
- 要发送的数据指针在哪里

这个示例测试的就是这件事。

---

## 4. 在真实主循环中怎么接

真实主循环一般长这样：

```uya
const result = uip_input(&state, &rt, -1, incoming_len, false, false, 0u16);
rt.flags = result.flags;
rt.len = result.len;

hello_on_connect(&rt);

if rt.slen > 0u16 || rt.len > 0u16 {
    var frame = ...;
    var send_len: u16 = rt.len;
    uip_arp_out(&arp, &frame, &send_len);
    tapdev_send(...);
}
```

更完整的语义是：

1. `uip_input(...)` 处理收到的 TCP/IP 包
2. `rt.flags` 里可能出现 `UIP_CONNECTED`
3. `hello_on_connect(&rt)` 检测到连接建立
4. `uip_send(...)` 把 `helloworld` 挂到发送缓冲语义上
5. `uip_arp_out(...)` 生成链路层头
6. 底层设备发出去

---

## 5. 如果你想改成“本地打印 helloworld”

不是发给网络，而是在本地终端打印，只要写成：

```uya
fn hello_on_connect(rt: &UipRuntime) void {
    if uip_connected(rt.flags) {
        printf("helloworld\n");
    }
}
```

这种适合做事件验证 demo。

---

## 6. 如果你想做“客户端连上来就收到 helloworld”

就保持发送版本，但通常建议加换行：

```uya
const msg: [byte: 12] = ['h','e','l','l','o','w','o','r','l','d','\r','\n'];
uip_send(rt, &msg[0], 12u16);
```

这样 telnet / nc 连进来时更容易看到结果。

---

## 7. 常见扩展

### 只在第一次连接时发一次
当前 `uip_connected(...)` 本身就表示“连接建立事件”，通常只会在建立瞬间触发一次。

### 收到数据后再回复
可以改成：

```uya
if uip_newdata(rt.flags) {
    uip_send(rt, &msg[0], 10u16);
}
```

### 连接建立后先打印，再发送
可以组合：

```uya
if uip_connected(rt.flags) {
    printf("client connected\n");
    uip_send(rt, &msg[0], 10u16);
}
```

---

## 8. 当前仓库里的现实情况

这个示例已经能作为**接口用法示例**阅读和 `check`。

但若要完全走到宿主 C 链接执行，当前仓库 `ports/uip/uip_core.uya` 仍有现存的生成/结构体一致性问题，与你之前问到的 `main` 不能直接跑是同一类问题。

所以：

- **作为 API 用法示例：可以直接参考**
- **作为当前仓库中完全执行的进程 demo：还需要继续收敛工具链/结构体问题**

---

## 9. 最小记忆版

如果你只记一件事，就记这个：

```uya
if uip_connected(rt.flags) {
    uip_send(rt, msg, len);
}
```

这就是用 `uya-uip` 实现“连接建立后发送内容”的核心模式。
