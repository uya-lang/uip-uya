# uIP-uya 设计说明（按 C 版 uIP 真实结构重建）

本文档不再采用“现代分层协议栈”的重构思路，而是以 **C 语言版 uIP 的真实设计** 为基准，说明如何用 **uya** 重新实现一遍 uIP。

目标不是重新发明一个新协议栈，而是：

> **尽可能忠实保留 C 版 uIP 的核心架构、数据流、资源模型与驱动方式，再用 uya 把它表达出来。**

这意味着 uya 版本应优先继承这些特征：

- 单一主报文缓冲区 `uip_buf`
- 以 `uip_process(flag)` 为中心的单核处理流程
- TCP / UDP / IP / ICMP 在核心文件内紧耦合处理
- 设备驱动与协议栈通过全局状态协作
- ARP 在核心外部单独处理，前置/后置调用
- 固定容量连接表、监听表、ARP 表
- 强依赖编译期配置裁剪代码与数据规模

---

## 1. 参考依据

本文设计参考公开 C 版 uIP 的实际源码组织，包括但不限于：

- `uip.c`
- `uip.h`
- `uip_arp.c`
- `uip_arp.h`
- `uiplib.c`
- `uipopt.h`
- `uip_arch.h`
- `uip-conf.h`（项目侧配置入口）

从这些源码可以确认，uIP 的本质不是“分层很好看”的协议栈，而是一个围绕 **最小 RAM / 最小 ROM / 最少函数边界** 设计出来的紧凑实现。

---

## 2. C 版 uIP 的真实设计特征

### 2.1 单一主缓冲区

uIP 的核心是全局缓冲区：

```text
uip_buf[UIP_BUFSIZE + 2]
uip_len
uip_appdata
uip_sappdata
```

其含义是：

- 网卡驱动把收到的数据直接写入 `uip_buf`
- 协议栈直接在这块缓冲区内解析 IP / TCP / UDP / ICMP 报头
- 应用层读取收到的数据，也直接从这块缓冲区取
- 要发送的数据也由应用通过 `uip_send()` 指定，再由协议栈补头、算校验、发出

这个设计是 uIP 能在极小 RAM 下运行的根本原因。

### 2.2 单核主处理函数

C 版核心逻辑集中在：

```text
uip_process(flag)
```

由不同入口宏驱动：

- `uip_input()` → `uip_process(UIP_DATA)`
- `uip_periodic(i)` → `uip_process(UIP_TIMER)`
- `uip_poll_conn(conn)` → `uip_process(UIP_POLL_REQUEST)`
- `uip_udp_periodic(i)` → `uip_process(UIP_UDP_TIMER)`
- UDP 发送也通过 flag 跳到特定发送路径

也就是说，uIP 的真实结构不是“多个层层调用的小模块”，而是：

> **一个核心状态机函数，根据 flag 决定是处理入站包、定时器、轮询还是发送。**

### 2.3 协议强耦合

在 `uip.c` 中，IP、ICMP、UDP、TCP 并不是严格分层隔离的：

- IP 头解析后立即决定走 ICMP / UDP / TCP
- TCP 解析、状态机推进、ACK / 重传 / 应用回调都在一个大流程中处理
- 为减少函数调用与参数传递开销，代码大量依赖宏、共享全局变量与 `goto`

这是一种**面向 ROM 优化**的设计，而不是面向模块边界优化的设计。

### 2.4 固定容量全局状态表

uIP 使用全局静态表保存协议状态：

```text
uip_conns[UIP_CONNS]
uip_listenports[UIP_LISTENPORTS]
uip_udp_conns[UIP_UDP_CONNS]
```

以及 ARP 表：

```text
arp_table[UIP_ARPTAB_SIZE]
```

这意味着：

- 没有动态分配
- 没有动态增长
- 所有容量在编译期决定
- 资源用量可预测

### 2.5 ARP 独立于 `uip.c`

uIP 对 Ethernet/ARP 的处理不是塞进 `uip_process()`，而是放在 `uip_arp.c` 中单独实现：

- `uip_arp_arpin()`：处理入站 ARP
- `uip_arp_out()`：在出站 IP 包前补 Ethernet 头或改写成 ARP request
- `uip_arp_timer()`：老化 ARP 表

驱动调用模式是：

```text
收包：
  if Ethernet type == IP:
    uip_arp_ipin()
    uip_input()
    if uip_len > 0:
      uip_arp_out()
      send()

  if Ethernet type == ARP:
    uip_arp_arpin()
    if uip_len > 0:
      send()
```

这说明 uIP 的 ARP 并不是协议核心内部的“通用链路层”，而是一个围绕 Ethernet 使用场景的外接模块。

---

## 3. uya 重写时应保留的总架构

如果目标是“用 uya 重新实现一遍 C 版 uIP”，那么总体设计不应改造成现代分层风格，而应保持以下结构：

```text
src/
  uip/
    uip.uya          // 对应 uip.c
    uip_types.uya    // 对应 uip.h 中的结构和头部定义
    uip_conf.uya     // 对应 uip-conf.h / uipopt.h 项目配置
    uip_arch.uya     // 对应 uip_arch.h
    uip_arp.uya      // 对应 uip_arp.c
    uip_arp_types.uya
    uiplib.uya       // 对应 uiplib.c
```

重点不是拆很多目录，而是尽量接近 C 版的组织方式。

---

## 4. uya 版的核心设计原则

### 4.1 保留“单核处理函数”

uya 版本应保留一个与 `uip_process(flag)` 等价的核心入口，例如：

```text
uip_process(flag: UipProcessFlag)
```

它负责：

- 处理收到的数据包
- 处理 TCP 周期定时器
- 处理 UDP 周期事件
- 处理 poll 请求
- 生成出站包

不要把它拆成很多彼此独立的高级对象，否则会偏离 uIP 的真实设计目标。

### 4.2 保留单一主缓冲区模型

uya 版本仍应保留：

```text
uip_buf
uip_len
uip_appdata
uip_sappdata
uip_conn
uip_udp_conn
uip_flags
```

只是表达方式从 C 的全局变量变成 uya 可接受的静态模块状态或单例状态容器。

但关键点不变：

- 整个协议栈围绕一块主报文缓冲区运作
- 不引入多 buffer 池
- 不引入每层复制
- 不做 socket 队列

### 4.3 保留面向宏/常量裁剪的配置模型

C 版 uIP 高度依赖：

- `UIP_CONNS`
- `UIP_UDP_CONNS`
- `UIP_LISTENPORTS`
- `UIP_ARPTAB_SIZE`
- `UIP_BUFSIZE`
- `UIP_UDP`
- `UIP_REASSEMBLY`
- `UIP_ACTIVE_OPEN`
- `UIP_STATISTICS`
- `UIP_LOGGING`

uya 版本也应该保留等价的**编译期配置项**，而不是改成完全运行时动态配置。

因为对于 uIP 来说，配置不仅是行为切换，更是 ROM / RAM 模型的一部分。

### 4.4 保留应用与协议栈的协作方式

C 版 uIP 的应用模型是：

- 协议栈调用应用
- 应用通过全局上下文读取当前连接状态
- 应用在合适时机调用 `uip_send()` 写出待发送数据
- 协议栈负责裁剪长度、补头、计算校验和

uya 版本如果要忠实重写，也应该采用类似方式，而不是直接设计成现代 socket API。

---

## 5. 建议的 uya 模块映射

## 5.1 `uip.uya`

对应 C 版：`uip.c`

职责：

- 全局状态定义
- `uip_init`
- `uip_process`
- `uip_connect`
- `uip_udp_new`
- `uip_listen` / `uip_unlisten`
- 校验和计算
- TCP / UDP / ICMP / IP 主流程
- 可能的分片重组逻辑

这是 uya 重写中的**核心文件**，应允许它保持相对集中，而不是强行拆散。

## 5.2 `uip_types.uya`

对应 C 版：`uip.h` 中的类型、头部结构、常量、宏替代

职责：

- IP 地址类型
- TCP / UDP 连接结构
- 报文头部结构
- 标志常量
- 枚举 / 常量定义
- `uip_input` / `uip_periodic` 这类宏的等价封装

## 5.3 `uip_conf.uya`

对应 C 版：`uipopt.h` + `uip-conf.h`

职责：

- 缓冲区大小
- TCP 连接数
- UDP 连接数
- 监听端口数
- ARP 表大小
- TCP MSS
- TTL
- 是否启用 UDP / ARP / REASSEMBLY / ACTIVE_OPEN

注意：

- 这些值应尽量在编译期固定
- 不要把它们做成运行时任意可变配置

## 5.4 `uip_arch.uya`

对应 C 版：`uip_arch.h`

职责：

- 字节序相关辅助
- 平台相关整数操作
- 可选的 32 位加法优化
- 可选的校验和平台优化

uya 版本应保留这层的“平台适配”角色，但不应扩展成复杂 HAL。

## 5.5 `uip_arp.uya`

对应 C 版：`uip_arp.c`

职责：

- ARP 表
- `uip_arp_init`
- `uip_arp_timer`
- `uip_arp_arpin`
- `uip_arp_out`
- Ethernet 头处理

注意：

- ARP 仍应作为独立模块存在
- 它不是通用链路层框架，只是面向 Ethernet 的 ARP 实现

## 5.6 `uiplib.uya`

对应 C 版：`uiplib.c`

职责：

- 简单辅助函数
- 如 IP 地址字符串转换等

这部分不应混进核心路径。

---

## 6. uya 版数据模型设计

虽然要忠实复刻 C 版 uIP，但 uya 版本仍需要一个适合语言表达的状态承载方式。建议采用：

```text
UipState
- uip_buf
- uip_len
- uip_appdata
- uip_sappdata
- uip_flags
- uip_conn
- uip_udp_conn
- uip_conns[]
- uip_udp_conns[]
- uip_listenports[]
- uip_hostaddr
- uip_draddr
- uip_netmask
- uip_ethaddr
- ipid
- iss
- temporary vars
```

但这里的 `UipState` 只是 **uya 对 C 全局变量集合的一种承载方式**，不是现代协议栈对象。

它的设计目标应当是：

- 与 C 版全局状态一一对应
- 方便映射 C 版逻辑
- 不引入多余间接层
- 允许编译器静态布局

### 6.1 连接表

应保留固定长度数组：

```text
uip_conns[UIP_CONNS]
uip_udp_conns[UIP_UDP_CONNS]
uip_listenports[UIP_LISTENPORTS]
```

不要改成：

- 动态 vec
- 哈希表
- 链表
- 堆分配对象池

### 6.2 当前连接指针语义

C 版有：

```text
uip_conn
uip_udp_conn
```

表示“当前正在处理的连接”。uya 版也应该保留这一语义，比如：

- 当前 TCP 连接索引
- 当前 UDP 连接索引
- 或可空引用

因为应用回调模型与 `uip_process()` 都依赖这个上下文。

### 6.3 应用数据指针语义

C 版通过：

```text
uip_appdata
uip_sappdata
```

让应用知道：

- 当前收到的数据在哪里
- 当前要发送的数据在哪里

uya 版可以不直接暴露裸指针，但必须保留等价语义，例如：

- 当前 app data offset
- 当前 send data reference

关键不是形式，而是行为必须与 C 版一致。

---

## 7. 真实调用流程应如何重建

## 7.1 初始化流程

对应 C 版：

- `uip_init()`
- `uip_arp_init()`
- 设置 IP / netmask / default router / MAC

uya 版应保持相同流程：

```text
uip_init()
uip_arp_init()
uip_sethostaddr(...)
uip_setnetmask(...)
uip_setdraddr(...)
uip_setethaddr(...)
```

## 7.2 收包路径

Ethernet 场景下，驱动逻辑应保持与 C 版一致：

```text
uip_len = device.recv_into(uip_buf)
if uip_len > 0:
  if eth.type == IP:
    uip_arp_ipin()   // 在标准 uIP 里通常为空宏
    uip_input()
    if uip_len > 0:
      uip_arp_out()
      device.send(uip_buf, uip_len)
  else if eth.type == ARP:
    uip_arp_arpin()
    if uip_len > 0:
      device.send(uip_buf, uip_len)
```

注意：这不是“层层分发框架”，而是驱动与协议栈的直接协作。

## 7.3 TCP 定时轮询路径

对应 C 版：

```text
for i in 0..UIP_CONNS:
  uip_periodic(i)
  if uip_len > 0:
    uip_arp_out()
    device.send(...)
```

uya 版也应保持这个模式，不要替换成复杂事件循环。

## 7.4 UDP 周期路径

对应 C 版：

```text
for i in 0..UIP_UDP_CONNS:
  uip_udp_periodic(i)
  if uip_len > 0:
    uip_arp_out()
    device.send(...)
```

## 7.5 ARP 定时器路径

对应 C 版：

```text
every 10 seconds:
  uip_arp_timer()
```

这条路径应单独保留。

---

## 8. 与 C 版模块的对照关系

| C 版模块 | uya 版建议模块 | 说明 |
|---|---|---|
| `uip.c` | `src/uip/uip.uya` | 核心重写目标，保留单核流程 |
| `uip.h` | `src/uip/uip_types.uya` | 类型、头部结构、常量、辅助入口 |
| `uipopt.h` | `src/uip/uip_conf.uya` | 默认配置与编译期裁剪 |
| `uip-conf.h` | `src/uip/uip_conf_project.uya` 或构建配置 | 项目侧覆盖配置 |
| `uip_arch.h` | `src/uip/uip_arch.uya` | 架构相关适配 |
| `uip_arp.c` | `src/uip/uip_arp.uya` | ARP 与 Ethernet 发包前处理 |
| `uip_arp.h` | `src/uip/uip_arp_types.uya` | Ethernet/ARP 类型与声明 |
| `uiplib.c` | `src/uip/uiplib.uya` | 辅助工具函数 |

---

## 9. 与我之前那版“分层设计”的根本区别

之前那版设计不适用于“重写 C 版 uIP”的原因在于，它默认了这些前提：

- 按网络层/传输层/调度层拆开
- 使用更现代的模块边界
- 弱化全局状态
- 弱化 `uip_process()` 单核入口
- 把 ARP 当作正常的链路层模块
- 倾向更友好的 API

但这与真实 uIP 的设计哲学不一致。

真实 uIP 的重点是：

- **不是优雅分层**，而是**最低资源成本**
- **不是解耦优先**，而是**代码尺寸优先**
- **不是通用 socket 模型**，而是**应用与协议栈紧耦合**

因此，如果目标是“用 uya 把 C 版 uIP 原样重做一遍”，正确方向应当是：

> **忠实复刻其主缓冲区模型、主流程模型、静态表模型、驱动协作模型，而不是先现代化再实现。**

---

## 10. 对 uya 实现的具体约束

为了真正贴近 C 版 uIP，uya 实现时建议遵循以下约束。

### 10.1 不引入动态内存

- 不使用 GC 管理协议对象
- 不使用运行时扩容容器
- 不为每个连接动态分配状态块

### 10.2 不引入多缓冲模型

- 只保留单一 `uip_buf`
- 不做 RX/TX 双大缓冲，除非目标平台必须如此
- 不做 per-socket 队列

### 10.3 不强行面向对象化

- 不把 TCP、UDP、IPv4、ARP 做成重量级实例对象
- 不引入复杂 trait 继承树
- 不在核心路径上追求抽象优雅

### 10.4 允许核心代码集中

- `uip.uya` 可以很大
- 可以保留与 C 版相似的控制流
- 可以保留共享临时变量、共享状态
- 必要时允许使用接近 C 逻辑的流程控制

### 10.5 host 测试与 MCU 产物分离

虽然架构上要忠实于 C 版，但仍然可以：

- 在 host 上写测试
- 在测试中构造 `uip_buf`
- 检查 `uip_len`、头部字段、状态表变化

但这些测试辅助不应改变核心实现模型。

---

## 11. 建议的实现顺序

如果目标是忠实重写 C 版 uIP，建议按 C 版组织顺序推进，而不是按抽象分层推进。

### 第一阶段：框架骨架

1. `uip_conf.uya`
2. `uip_types.uya`
3. `uip_arch.uya`
4. `uip.uya` 中的全局状态与 `uip_init()`
5. `uip_arp.uya` 中的 ARP 表与 `uip_arp_init()`

### 第二阶段：基础 IP/ICMP 路径

1. 报头结构定义
2. `uip_process(UIP_DATA)` 的基础入站流程
3. IPv4 校验
4. ICMP echo reply
5. `uip_arp_out()` 出站封装

### 第三阶段：UDP

1. `uip_udp_conns[]`
2. `uip_udp_new()`
3. UDP 收包分发
4. UDP 发送路径
5. `uip_udp_periodic()`

### 第四阶段：TCP

1. `uip_conns[]`
2. `uip_listen()` / `uip_unlisten()`
3. `uip_connect()`
4. SYN / ACK / FIN / RST 处理
5. 定时器与重传
6. 应用回调路径

### 第五阶段：可选特性

1. IP reassembly
2. statistics
3. logging
4. 架构特定优化校验和

---

## 12. 总结

如果项目目标是：

> **“使用 uya 从零重新实现 C 版本的 uIP 协议栈”**

那么最合适的设计路线不是“重新设计一个更现代的协议栈架构”，而是：

- 以 `uip.c` 为核心蓝本
- 以 `uip_buf + uip_len + uip_process(flag)` 为运行时中心
- 以固定静态表为资源模型
- 以 ARP 外接模块为 Ethernet 适配方式
- 以编译期裁剪为配置机制
- 以应用紧耦合协作为接口模型

一句话概括：

> **uya 版应当是 C 版 uIP 的语义级重写，而不是理念继承后的重新架构。**
