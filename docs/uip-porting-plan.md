# uIP-uya 迁移清单（C 版 uIP → uya）

本文档用于把 C 语言版 uIP 拆解成一份可执行的迁移计划，目标是：

> **按文件、按状态、按函数，把 C 版 uIP 逐步迁移到 uya，而不是在实现过程中临时决定结构。**

本清单以公开 C 版 uIP 的典型模块为参考：

- `uip.c`
- `uip.h`
- `uip_arp.c`
- `uip_arp.h`
- `uipopt.h`
- `uip_arch.h`
- `uiplib.c`

---

## 1. 总体迁移目标

uya 版不是做“uIP 风格协议栈”，而是做“uIP 的 uya 重写版”。

因此迁移时遵循以下原则：

- 优先保持 **数据模型一致**
- 优先保持 **主流程一致**
- 优先保持 **驱动协作方式一致**
- 优先保持 **编译期配置模型一致**
- 不为了工程美观而改变资源模型

可接受的变化主要只有两类：

1. **语言表达变化**
   - 例如宏改为常量、枚举、内联函数
   - 裸指针改为偏移或受控引用

2. **测试支撑变化**
   - 为 host 测试增加辅助入口
   - 但不能改变协议栈核心行为模型

---

## 2. 建议的 uya 文件布局

建议按接近 C 版的方式落地：

```text
src/uip/
  uip.uya
  uip_types.uya
  uip_conf.uya
  uip_arch.uya
  uip_arp.uya
  uip_arp_types.uya
  uiplib.uya
```

对应关系：

| C 版 | uya 版 |
|---|---|
| `uip.c` | `src/uip/uip.uya` |
| `uip.h` | `src/uip/uip_types.uya` |
| `uipopt.h` + `uip-conf.h` | `src/uip/uip_conf.uya` |
| `uip_arch.h` | `src/uip/uip_arch.uya` |
| `uip_arp.c` | `src/uip/uip_arp.uya` |
| `uip_arp.h` | `src/uip/uip_arp_types.uya` |
| `uiplib.c` | `src/uip/uiplib.uya` |

---

## 3. `uip.h` → `uip_types.uya`

这是第一优先级文件，因为后续几乎所有实现都依赖它。

## 3.1 需要迁移的类型

### 地址类型

- `uip_ip4addr_t`
- `uip_ip6addr_t`
- `uip_ipaddr_t`

uya 版建议：

- 先只实现 IPv4 路径所需表示
- 保留 IPv6 扩展空间，但不要阻塞 IPv4 重写

### 连接结构

- `struct uip_conn`
- `struct uip_udp_conn`

需要逐字段迁移，并保留字段布局语义，例如：

- TCP state flags
- local/remote port
- remote IP
- sequence / ack tracking
- retransmission counters
- timers
- MSS / initial MSS
- app state hooks（如原版需要）

### 报头结构

需要迁移常见的协议头结构：

- IPv4 header
- TCP/IP combined header
- UDP/IP combined header
- ICMP/IP combined header

这些结构不一定要 1:1 复制成“高级对象”，但必须能支持与 C 版等价的字段读写。

### 标志与常量

需要迁移的典型常量包括：

- TCP 标志位：`TCP_FIN` `TCP_SYN` `TCP_RST` `TCP_ACK` `TCP_URG` 等
- ICMP 类型：`ICMP_ECHO` `ICMP_ECHO_REPLY`
- 处理标志：`UIP_DATA` `UIP_TIMER` `UIP_POLL_REQUEST` `UIP_UDP_TIMER` 等
- TCP 状态：`UIP_CLOSED` 等全部状态值

### 全局接口宏

C 版常见宏：

- `uip_input()`
- `uip_periodic(i)`
- `uip_periodic_conn(conn)`
- `uip_poll_conn(conn)`
- `uip_udp_periodic(i)`
- `uip_udp_periodic_conn(conn)`

uya 版建议改为：

- 小函数
- 内联函数
- 或直接的辅助入口

但行为要和原版保持一致。

## 3.2 迁移完成标准

完成 `uip_types.uya` 后，应满足：

- 能声明整个 uIP 核心状态
- 能表达全部核心报头字段
- 能替代大部分 `uip.h` 中的结构声明和常量宏

---

## 4. `uipopt.h` / `uip-conf.h` → `uip_conf.uya`

这是第二优先级，因为资源模型和代码裁剪都依赖它。

## 4.1 需要迁移的配置项

### 固定地址与链路参数

- `UIP_FIXEDADDR`
- `UIP_FIXEDETHADDR`
- 静态 host / router / netmask / MAC 参数

### IP 相关

- `UIP_TTL`
- `UIP_REASSEMBLY`
- `UIP_REASS_MAXAGE`

### UDP 相关

- `UIP_UDP`
- `UIP_UDP_CHECKSUMS`
- `UIP_UDP_CONNS`

### TCP 相关

- `UIP_ACTIVE_OPEN`
- `UIP_CONNS`
- `UIP_LISTENPORTS`
- `UIP_URGDATA`
- `UIP_RTO`
- `UIP_MAXRTX`
- `UIP_MAXSYNRTX`
- `UIP_TCP_MSS`
- `UIP_RECEIVE_WINDOW`
- `UIP_TIME_WAIT_TIMEOUT`

### ARP 相关

- `UIP_ARPTAB_SIZE`
- `UIP_ARP_MAXAGE`

### 通用配置

- `UIP_BUFSIZE`
- `UIP_STATISTICS`
- `UIP_LOGGING`
- `UIP_BROADCAST`
- `UIP_LLH_LEN`

## 4.2 uya 版实现建议

这些配置应尽量保留为：

- 编译期常量
- 条件编译 feature
- 构建 profile 常量

不要改成完全运行时动态配置结构，否则会背离 uIP 的设计。

## 4.3 迁移完成标准

完成 `uip_conf.uya` 后，应满足：

- 可以据此分配所有静态数组
- 可以据此裁剪 UDP / ARP / 重组等代码路径
- 可以据此推导 MSS / 缓冲区上限等常量

---

## 5. `uip_arch.h` → `uip_arch.uya`

这个文件是平台适配边界。

## 5.1 需要迁移的能力

- 字节序转换
- 平台整数类型兼容层
- 可选的 32 位加法优化
- 可选的校验和架构优化入口

## 5.2 uya 版实现建议

- 如果 uya 本身已有稳定整数类型，则无需机械复制类型定义
- 但仍应保留“架构可覆写”的能力，例如：
  - `add32`
  - `ip_checksum`
  - `tcp_checksum`

## 5.3 迁移完成标准

完成 `uip_arch.uya` 后，应满足：

- 核心校验和与字节序代码可工作
- 平台差异不污染 `uip.uya` 主流程

---

## 6. `uip.c` → `uip.uya`

这是整个项目的核心，也是迁移工作量最大的部分。

## 6.1 需要先迁移的全局状态

根据 C 版源码，至少需要迁移这些核心状态：

### 地址与主机配置

- `uip_hostaddr`
- `uip_draddr`
- `uip_netmask`
- `uip_ethaddr`

### 主缓冲区与应用数据语义

- `uip_buf`
- `uip_len`
- `uip_appdata`
- `uip_sappdata`
- `uip_slen`

如后续支持 urgent data，还包括：

- `uip_urgdata`
- `uip_urglen`
- `uip_surglen`

### 核心连接上下文

- `uip_flags`
- `uip_conn`
- `uip_conns[]`
- `uip_listenports[]`
- `uip_udp_conn`
- `uip_udp_conns[]`

### 协议内部状态

- `ipid`
- `iss`
- `lastport`
- 临时累加器 `uip_acc32`
- 若干局部共享临时变量

### 可选特性状态

- 分片重组缓存
- 统计结构
- logging 钩子

## 6.2 需要迁移的基础函数

### 初始化与配置

- `uip_init()`
- `uip_setipid()`
- 主机地址相关 getter/setter 等价实现

### TCP / UDP 连接管理

- `uip_connect()`
- `uip_udp_new()`
- `uip_listen()`
- `uip_unlisten()`

### 校验和相关

- `uip_add32()`
- `uip_chksum()`
- `uip_ipchksum()`
- `uip_tcpchksum()`
- `uip_udpchksum()`
- 内部 `upper_layer_chksum()`

### 分片重组（可选）

- `uip_reass()`

### 核心处理函数

- `uip_process(flag)`

这是最关键的迁移目标。

## 6.3 `uip_process(flag)` 的迁移拆分顺序

虽然最终要保留单核主流程，但迁移时建议按下面顺序逐段完成。

### 第 1 段：入口与上下文建立

先迁移：

- 根据 flag 进入不同路径
- 初始化 `uip_appdata` / `uip_sappdata`
- 建立当前连接上下文

### 第 2 段：IP 入站校验

迁移：

- IP 头长度检查
- 版本检查
- IP 校验和检查
- 分片判断 / 可选重组逻辑
- 目标地址检查

### 第 3 段：ICMP 最小支持

迁移：

- ICMP echo request
- ICMP echo reply 生成
- 必要的错误丢弃路径

### 第 4 段：UDP 路径

迁移：

- UDP 头解析
- UDP checksum（若启用）
- 匹配 `uip_udp_conns[]`
- 交付应用
- 发送路径处理

### 第 5 段：TCP 入站基础

迁移：

- 匹配连接
- 未命中时查监听端口
- SYN / ACK / RST 基础分支
- 初步状态机推进

### 第 6 段：TCP 完整状态机

迁移：

- ESTABLISHED 数据处理
- FIN / CLOSE / ABORT / TIME_WAIT 路径
- 重传 / 超时 / 窗口更新
- 应用事件触发

### 第 7 段：周期处理路径

迁移：

- `UIP_TIMER`
- `UIP_POLL_REQUEST`
- `UIP_UDP_TIMER`
- 发送时机与重传路径

## 6.4 `uip.uya` 迁移完成标准

完成后应满足：

- 单缓冲区模型成立
- `uip_process(flag)` 能覆盖输入、轮询、定时和发送路径
- TCP / UDP / ICMP 最小功能可跑通
- 驱动可按原版方式调用

---

## 7. `uip_arp.h` / `uip_arp.c` → `uip_arp_types.uya` / `uip_arp.uya`

这部分应独立于 `uip.uya` 实现，但与它共享 `uip_buf` / `uip_len` / 地址配置。

## 7.1 需要迁移的数据结构

- Ethernet header
- ARP header
- ARP table entry

## 7.2 需要迁移的状态

- `arp_table[UIP_ARPTAB_SIZE]`
- `arptime`
- 查找用临时变量

## 7.3 需要迁移的函数

- `uip_arp_init()`
- `uip_arp_timer()`
- `uip_arp_update()`
- `uip_arp_arpin()`
- `uip_arp_out()`

## 7.4 行为重点

### `uip_arp_arpin()`

要保留：

- 入站 ARP request 若目标是本机，则直接在 `uip_buf` 上改写成 ARP reply
- 入站 ARP reply 若目标是本机，则更新 ARP 表
- 返回时通过 `uip_len` 表示是否要发包

### `uip_arp_out()`

要保留：

- 对本地网络目标，直接查 ARP 表
- 若目标不在本地网络，则改查默认路由地址
- 查到表项则补 Ethernet 头
- 查不到则把当前 IP 包覆盖成 ARP request
- 丢失的 IP 包依赖 TCP 上层重传恢复

这一点非常关键，因为这是 uIP 省 RAM 的典型设计。

## 7.5 迁移完成标准

完成后应满足：

- Ethernet 场景下可按原版驱动流程工作
- ARP request / reply / cache aging 可运行
- `uip_arp_out()` 可直接配合 `uip_process()` 产出的 IP 包使用

---

## 8. `uiplib.c` → `uiplib.uya`

这是低优先级文件。

## 8.1 需要迁移的内容

- IP 地址字符串转换等辅助函数

## 8.2 原则

- 不进入核心热路径
- 不影响协议栈核心资源模型
- 可优先只在 host 调试和测试中使用

---

## 9. 驱动调用模型迁移

这是实现时最容易被“现代框架化”破坏的部分，必须单独强调。

## 9.1 Ethernet 收包流程

应保持与 C 版一致：

```text
uip_len = device.recv_into(uip_buf)
if uip_len > 0:
  if eth.type == IP:
    uip_arp_ipin()
    uip_input()
    if uip_len > 0:
      uip_arp_out()
      device.send(uip_buf, uip_len)
  else if eth.type == ARP:
    uip_arp_arpin()
    if uip_len > 0:
      device.send(uip_buf, uip_len)
```

## 9.2 TCP 周期处理流程

```text
for each conn:
  uip_periodic(conn)
  if uip_len > 0:
    uip_arp_out()
    device.send(...)
```

## 9.3 UDP 周期处理流程

```text
for each udp conn:
  uip_udp_periodic(conn)
  if uip_len > 0:
    uip_arp_out()
    device.send(...)
```

## 9.4 ARP 老化流程

```text
every 10 seconds:
  uip_arp_timer()
```

---

## 10. 建议的实现里程碑

## M1：最小骨架

完成：

- `uip_conf.uya`
- `uip_types.uya`
- `uip_arch.uya`
- `uip.uya` 基础状态
- `uip_arp.uya` 基础状态

验收：

- 编译通过
- 静态数组和基础状态可初始化

## M2：ARP + IPv4 + ICMP

完成：

- `uip_arp_arpin()`
- `uip_arp_out()`
- `uip_process(UIP_DATA)` 的 IPv4 / ICMP 最小路径

验收：

- ARP request 可回复
- ICMP echo 可回复

## M3：UDP

完成：

- `uip_udp_new()`
- UDP 入站匹配
- UDP 出站路径
- UDP 周期处理

验收：

- 单端口 UDP 收发可跑通

## M4：TCP 最小建连

完成：

- `uip_listen()` / `uip_unlisten()`
- SYN / SYN-ACK / ACK 基础流程
- 最小连接状态推进

验收：

- 能建立最小 TCP 连接

## M5：TCP 数据收发与重传

完成：

- 数据段处理
- ACK 路径
- 重传计时
- 超时处理
- close / abort / time_wait

验收：

- 最小 TCP 回显或简单应用可跑通

## M6：可选特性

完成：

- reassembly
- statistics
- logging
- 架构优化路径

---

## 11. 每阶段测试建议

## 类型与配置阶段

- 配置常量边界检查
- 缓冲区大小与 MSS 关系检查
- 连接表大小与索引边界检查

## ARP / ICMP 阶段

- ARP request → ARP reply
- ARP reply 更新缓存
- ICMP echo request → echo reply
- 非本机目标包丢弃

## UDP 阶段

- 正常 UDP 输入匹配
- 无匹配端口丢弃
- 发送数据报头部正确
- 周期发送路径正确

## TCP 阶段

- listen 命中
- SYN 建连
- 重复 ACK
- 超时重传
- FIN 关闭
- 非法段丢弃 / RST

---

## 12. 最后建议

实现这个项目时，最容易犯的错误不是“代码写错”，而是：

> **写着写着把 uIP 重写成了另一套更现代、但不再是 uIP 的协议栈。**

所以迁移时应始终自检：

- 这个变化是因为 uya 语法需要，还是我在偷偷改架构？
- 这个辅助层是为了实现原版行为，还是为了满足现代工程洁癖？
- 这个抽象是否增加了 RAM / ROM / 控制流复杂度？

如果目标是忠实重写 C 版 uIP，那么最重要的不是“代码看起来更漂亮”，而是：

- 结构保持相似
- 数据流保持相似
- 资源模型保持相似
- 驱动调用方式保持相似

这才是后续实现应当坚持的主线。
