# uIP Uya 移植

版本：v0.1.0

本仓库在 `ports/uip/` 目录下提供对原始 C 版本 `uIP`（对照源目录：`/home/ubuntu/Documents/uip/uip/`）的 Uya 语言移植。当前核心实现集中在 `ports/uip/uiplib.uya`，测试位于 `ports/uip/tests/`。

## 当前内容

- 核心实现：`ports/uip/uiplib.uya`
- 测试目录：`ports/uip/tests/`

## 原始 uIP 与当前仓库移植对照表

| 原始文件 | 当前状态 | Uya 对应实现 / 说明 |
|---|---|---|
| `uip.c` | 部分移植 | `ports/uip/uiplib.uya`：已覆盖 TCP/UDP 核心状态机、连接管理、运行时处理；IPv6、reassembly、statistics、logging、urgent data 等仍未完整覆盖 |
| `uip.h` | 已移植 | `ports/uip/uiplib.uya`：常量、结构、协议头、状态定义 |
| `uipopt.h` | 已移植 | `ports/uip/uiplib.uya`：以 `export const` 形式内联配置 |
| `uip_arch.h` | 已移植 | `ports/uip/uiplib.uya`：字节序/地址辅助逻辑已吸收 |
| `uiplib.c` | 已移植 | `ports/uip/uiplib.uya`：`uiplib_ipaddrconv` |
| `uiplib.h` | 已移植 | `ports/uip/uiplib.uya`：相关导出函数已覆盖 |
| `timer.c` | 已移植 | `ports/uip/uiplib.uya`：`timer_set/reset/restart/expired` |
| `timer.h` | 已移植 | `ports/uip/uiplib.uya`：`Timer` 结构与接口 |
| `uip_arp.c` | 主要移植 | `ports/uip/uiplib.uya`：ARP 表、ARP 输入输出、地址更新；部分原始细节路径未逐分支复刻 |
| `uip_arp.h` | 已移植 | `ports/uip/uiplib.uya`：ARP 常量、结构、接口 |
| `uip-neighbor.c` | 已移植 | `ports/uip/uiplib.uya`：邻居表初始化、老化、更新、查找 |
| `uip-neighbor.h` | 已移植 | `ports/uip/uiplib.uya`：`UipNeighborState` / `UipNeighborEntry` / `UipNeighborAddr` |
| `uip-fw.c` | 主要移植 | `ports/uip/uiplib.uya`：转发缓存、接口注册、输出、转发、周期处理；设备级输出/广播/ICMP time exceeded 细节未完整覆盖 |
| `uip-fw.h` | 已移植 | `ports/uip/uiplib.uya`：`UipFwState` / `UipFwNetif` / 常量 |
| `uip-split.c` | 主要移植 | `ports/uip/uiplib.uya`：`uip_split_output`；与真实 `tcpip_output()` / `uip_appdata` 路径的完整一致性未完全复刻 |
| `uip-split.h` | 已移植 | `ports/uip/uiplib.uya`：拆分发送接口与追踪结构 |
| `pt.h` | 最小兼容移植 | `ports/uip/uiplib.uya`：`Pt`、`pt_init`、`pt_wait_until`、`pt_yield`、`pt_exit`、`pt_end`、`pt_schedule`；`PT_BEGIN/WAIT_THREAD/SPAWN/RESTART/YIELD_UNTIL` 等完整控制流语义未真正复刻 |
| `psock.c` | 最小兼容移植 | `ports/uip/uiplib.uya`：`psock_init`、`psock_send`、`psock_readbuf`、`psock_readto`；`psock_generator_send`、完整 ACK/重传/状态机语义未完整复刻 |
| `psock.h` | 最小兼容移植 | `ports/uip/uiplib.uya`：`Psock` / `PsockBuf` 与导出接口 |
| `lc.h` | Uya 等价层 | `ports/uip/uiplib.uya`：`Lc`、`lc_init`、`lc_set`、`lc_resume`、`lc_end` |
| `lc-switch.h` | Uya 等价层 | 未复刻 C 宏 `switch/case` continuation 技巧，改为 `Lc` 状态承载 |
| `lc-addrlabels.h` | 无需单独移植 | 当前采用 `Lc` 结构而非 C 预处理宏标签机制 |
| `clock.h` | 未单独移植 | 当前 uIP 端口未依赖单独时钟抽象，计时能力由 `Timer` 覆盖 |
| `Makefile.include` | 无需移植 | 构建由当前仓库 Uya 工具链负责 |

## 还未真正完整移植的功能清单

以下内容虽然已有部分实现或等价替代，但**尚未达到原始 C 版本的完整语义覆盖**：

### A. `psock` 完整语义未补齐
- `psock_generator_send()` 未实现
- `send_data()` / `data_acked()` 的完整 ACK / 重传配合未复刻
- 原始 `psock` 状态机中的完整状态流转尚未完整覆盖：
  - `STATE_ACKED`
  - `STATE_READ`
  - `STATE_BLOCKED_NEWDATA`
  - `STATE_BLOCKED_CLOSE`
  - `STATE_BLOCKED_SEND`
  - `STATE_DATA_SENT`

### B. `pt` 完整控制流模型未补齐
- 未真正复刻这些原始能力：
  - `PT_BEGIN`
  - `PT_WAIT_WHILE`
  - `PT_WAIT_THREAD`
  - `PT_SPAWN`
  - `PT_RESTART`
  - `PT_YIELD_UNTIL`
- 当前仅提供最小状态兼容层，不是完整 protothread 控制流实现

### C. `lc-switch` 宏 continuation 技术未复刻
- 当前 `Lc` 仅保存 continuation 状态
- 原始 `LC_RESUME/LC_SET` 基于 `switch/case + __LINE__` 的恢复机制未真正移植

### D. `uip.c` 缺失能力
- IPv6 协议路径未完整移植
- ICMPv6 / NS / NA 未完整移植
- IP fragmentation / reassembly 未完整移植
- `UIP_STATISTICS` 统计累积未完整移植
- `UIP_LOGGING` 日志钩子未完整移植
- `UIP_URGDATA` / urgent data 未完整移植
- 完整 `uip_process()` 全分支语义仍属于裁剪版实现

### E. `uip-fw` / `uip-split` 的完整设备级行为未补齐
- `uip-fw`：广播路径、ICMP time exceeded 构造、与真实网卡输出回调的完整行为未完全复刻
- `uip-split`：与真实 `tcpip_output()`、`uip_appdata` 搬移和完整校验和路径的一致性仍是简化版

## 建议补齐顺序

建议按收益和实现风险排序：

1. `psock` 完整状态机 + `psock_generator_send`
2. `pt/lc` 更接近原版的控制流层
3. `uip.c` 的 reassembly / statistics / logging / urgent data
4. IPv6 路径（若项目范围需要）

## 已拆分测试

为避免 TCP 与 UDP 测试相互干扰，测试已按职责拆分：

- `ports/uip/tests/uip_core_base_test.uya`：基础类型、地址、校验和、定时器等核心能力
- `ports/uip/tests/state_and_timer_test.uya`：状态初始化、监听、连接分配、UDP 连接管理
- `ports/uip/tests/uip_tcp_core_test.uya`：TCP 核心处理逻辑
- `ports/uip/tests/uip_tcp_handshake_test.uya`：TCP 握手与状态迁移
- `ports/uip/tests/udp_test.uya`：UDP 收发与路由逻辑
- `ports/uip/tests/uip_arp_test.uya` / `ports/uip/tests/arp_test.uya`：ARP 相关行为
- `ports/uip/tests/uiplib_ipaddrconv_test.uya`：`uiplib_ipaddrconv` 聚焦测试
- `ports/uip/tests/core_primitives_test.uya`：部分基础原语测试
- `ports/uip/tests/uip_neighbor_test.uya`：邻居表初始化、老化、更新、查找与替换策略
- `ports/uip/tests/uip_fw_test.uya`：转发接口选择、默认路由、TTL 递减与去重缓存
- `ports/uip/tests/uip_split_test.uya`：满尺寸 TCP 报文拆分发送
- `ports/uip/tests/lc_test.uya`：local continuation 最小状态层
- `ports/uip/tests/pt_test.uya`：protothread 最小状态机行为
- `ports/uip/tests/psock_test.uya`：protosocket 初始化、发送、读缓冲与读到标记

## 运行方式

在仓库根目录执行：

```bash
./uya/bin/uya test ports/uip/tests/uip_core_base_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/state_and_timer_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_core_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_handshake_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/udp_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_arp_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_neighbor_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_fw_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/uip_split_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/lc_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/pt_test.uya ports/uip/uiplib.uya
./uya/bin/uya test ports/uip/tests/psock_test.uya ports/uip/uiplib.uya
```

全量回归可执行：

```bash
for f in ports/uip/tests/*.uya; do
  ./uya/bin/uya test "$f" ports/uip/uiplib.uya || exit 1
done
```

## 移植范围说明

当前 `ports/uip/uiplib.uya` 覆盖内容包括：

- uIP 常量、类型与运行时状态定义
- IPv4 地址辅助函数
- 字节序与校验和计算
- TCP 基础状态机与部分报文构造逻辑
- UDP 连接匹配、输入输出处理
- ARP 状态与基本操作
- 邻居表 `uip-neighbor`
- 转发模块 `uip-fw`
- TCP 拆分发送 `uip-split`
- local continuation 等价层 `lc`
- protothread 最小运行模型 `pt`
- protosocket 最小兼容实现 `psock`
- 定时器与连接初始化能力

## 说明

- 当前 `pt` / `psock` / `lc` 为按 Uya 语言规则实现的最小兼容版本，不是对原始 C 宏控制流的逐字节直译。
- `lc-switch.h` 在 Uya 中采用显式状态结构替代，而不是保留 C 宏 `switch/case` continuation 技巧。
- 目前按测试文件分别编译/执行，暂不做聚合编译。
- 若后续继续统一修复，可在现有拆分基础上逐个回归测试。
