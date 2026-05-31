# uIP Uya 移植

版本：v0.1.0

本仓库在 `ports/uip/` 目录下提供对原始 C 版本 `uIP`（对照源目录：`/home/ubuntu/Documents/uip/uip/`）的 Uya 语言移植。当前主实现已按职责拆分到 `ports/uip/uip_base.uya`、`ports/uip/uip_core.uya`、`ports/uip/uip_proto.uya`、`ports/uip/uip_arp.uya`、`ports/uip/uip_fw_core.uya`，`ports/uip/uiplib.uya` 保留为兼容入口；测试位于 `ports/uip/tests/`。

## 当前内容

- 兼容入口：`ports/uip/uiplib.uya`
- 主模块：`ports/uip/uip_base.uya` / `ports/uip/uip_core.uya` / `ports/uip/uip_proto.uya` / `ports/uip/uip_arp.uya` / `ports/uip/uip_fw_core.uya`
- 测试目录：`ports/uip/tests/`

## 当前进展摘要

相对原始 C 版 uIP，本仓库当前状态可概括为：

- `uip.c` 主流程已完成大部分核心 TCP/UDP 语义迁移，已覆盖 ACK / NEWDATA / CLOSE / ABORT / CONNECTED、RST/FIN/ACK 优先级、`ack_outstanding`、timer/rexmit/timeout/TIME_WAIT 等主路径与边界测试
- `psock` 已完成 send/read/generator 事件桥接、current-event 视图、delimiter 完成条件，以及 close/timed_out/aborted 统一关闭语义
- `pt` 已补充显式 resume-point/helper 风格的替代能力与迁移模板，`Lc` 显式状态层作为 Uya 端口的 continuation 等价方案已定稿
- IPv4 fragmentation/reassembly 已覆盖 duplicate / overlap / timeout / 多片 bitmap、重组输出模型、IHL-sensitive payload 读取与 timer tick 语义
- statistics / logging / urgent data 已具备运行时等价层，并补齐 TCP/UDP/IPv6/runtime/timer 联动测试
- `uip-fw` / `uip-split` / IPv6 已按当前端口目标补齐实现与测试矩阵

## 原始 uIP 与当前仓库移植对照表

| 原始文件 | 当前状态 | Uya 对应实现 / 说明 |
|---|---|---|
| `uip.c` | 已按当前端口目标完成 | 主实现已拆分到 `ports/uip/uip_core.uya`；已覆盖 TCP/UDP 核心状态机、连接管理、ACK/NEWDATA/CLOSE/ABORT/CONNECTED、RST/FIN/ACK 优先级、`ack_outstanding`、timer/rexmit/timeout/TIME_WAIT、UDP timer、IPv6 runtime 分类、statistics/logging/urgent 等端口目标语义 |
| `uip.h` | 已移植 | 常量、结构、协议头、状态定义已收敛到 `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` |
| `uipopt.h` | 已移植 | 以 `export const` 形式内联配置 |
| `uip_arch.h` | 已移植 | 字节序/地址辅助逻辑已吸收 |
| `uiplib.c` | 已移植 | `ports/uip/uiplib.uya` / `ports/uip/uip_core.uya`：`uiplib_ipaddrconv` |
| `uiplib.h` | 已移植 | 相关导出函数已覆盖 |
| `timer.c` | 已移植 | `ports/uip/uip_proto.uya`：`timer_set/reset/restart/expired` |
| `timer.h` | 已移植 | `ports/uip/uip_proto.uya`：`Timer` 结构与接口 |
| `uip_arp.c` | 已移植 | `ports/uip/uip_arp.uya`：ARP 表、ARP 输入输出、地址更新；已对齐原版 aging / 更新时间戳 / 满表替换 / request-reply 路径 |
| `uip_arp.h` | 已移植 | `ports/uip/uip_arp.uya`：ARP 常量、结构、接口 |
| `uip-neighbor.c` | 已移植 | `ports/uip/uip_fw_core.uya`：邻居表初始化、老化、更新、查找 |
| `uip-neighbor.h` | 已移植 | `ports/uip/uip_fw_core.uya`：`UipNeighborState` / `UipNeighborEntry` / `UipNeighborAddr` |
| `uip-fw.c` | 已按当前端口目标完成 | `ports/uip/uip_fw_core.uya`：转发缓存、接口注册、输出、转发、周期处理、broadcast fanout、TTL expiry → ICMP time exceeded、default/nondefault output |
| `uip-fw.h` | 已移植 | `ports/uip/uip_fw_core.uya`：`UipFwState` / `UipFwNetif` / 常量 |
| `uip-split.c` | 已按当前端口目标完成 | `ports/uip/uip_fw_core.uya`：`uip_split_output`；已覆盖 second-half appdata 搬移、second-segment sequence 递增、non-max frame 单次发送语义 |
| `uip-split.h` | 已移植 | `ports/uip/uip_fw_core.uya`：拆分发送接口与追踪结构 |
| `pt.h` | 已按当前端口目标完成 | 主实现位于 `ports/uip/uip_proto.uya`：提供 `pt_resume`、`pt_set_resume`、`pt_clear_resume`、`pt_wait_at`、`pt_wait_thread_at`、`pt_spawn_at`、`pt_wait_thread`、`pt_spawn`、`pt_restart`、`pt_yield_until` 等 helper 风格迁移能力 |
| `psock.c` | 已按当前端口目标完成 | 主实现位于 `ports/uip/uip_proto.uya`：已覆盖 `psock_init`、`psock_send`、`psock_generator_send`、`psock_readbuf`、`psock_readto`、ACK/重传/close/exit 状态机、事件桥接、current-event 视图与统一关闭语义 |
| `psock.h` | 已按当前端口目标完成 | `ports/uip/uip_proto.uya`：`Psock` / `PsockBuf`、事件桥接接口与 current-event 视图已完成并由独立 bridge/edge 测试覆盖 |
| `lc.h` | Uya 等价层 | `ports/uip/uip_proto.uya`：`Lc`、`lc_init`、`lc_set`、`lc_resume`、`lc_end` |
| `lc-switch.h` | 已按当前端口目标完成 | 当前以 `Lc` 显式状态承载 continuation 语义，作为 Uya 端口的等价层定稿 |
| `lc-addrlabels.h` | 无需单独移植 | 当前采用 `Lc` 结构而非 C 预处理宏标签机制 |
| `clock.h` | 未单独移植 | 当前 uIP 端口未依赖单独时钟抽象，计时能力由 `Timer` 覆盖 |
| `Makefile.include` | 无需移植 | 构建由当前仓库 Uya 工具链负责 |

## 模块拆分计划（进行中）

为降低 `ports/uip/uiplib.uya` 的耦合度，仓库已拆分出以下模块：

- `ports/uip/uip_base.uya`：公共常量、类型、头结构、地址/校验和等基础能力
- `ports/uip/uip_core.uya`：核心运行时、TCP/UDP、logging、urgent、reassembly
- `ports/uip/uip_arp.uya`：ARP 状态与 `uip_arp_*`
- `ports/uip/uip_fw_core.uya`：neighbor、fw、split
- `ports/uip/uip_proto.uya`：`lc` / `pt` / `psock` / `timer`

当前阶段为**兼容拆分进行中**：

- `ports/uip/uiplib.uya` 仍保留历史实现，继续作为兼容入口
- 新增模块已可作为更小的测试编译入口使用
- 为避免一次性大改导致回归，当前**尚未删除 `uiplib.uya` 中的重复实现**；后续应按模块迁移完成度逐步收敛为聚合/兼容层

## 尚未完全对齐原版语义的功能清单

以下内容虽然已有部分实现或等价替代，但**尚未达到原始 C 版本的完整语义覆盖**：

### A. `psock` 端口语义
- 已完成：
  - `psock_send()` / `psock_generator_send()` / `psock_readbuf()` / `psock_readto()`
  - ACK / 重传 / close / exit 基本状态机
  - send/read/generator 事件桥接
  - `close` / `timed_out` / `aborted` 统一关闭语义
  - `ack` / `poll` / `rexmit` / `connected` + `newdata/readto` 边界小测试
- 当前以端口测试矩阵为准，采用 event-driven helper 风格语义

### B. `pt` 端口语义
- 已具备显式 helper 风格迁移能力：
  - `pt_resume`
  - `pt_set_resume`
  - `pt_clear_resume`
  - `pt_wait_at`
  - `pt_wait_thread_at`
  - `pt_spawn_at`
  - `pt_wait_while`
  - `pt_wait_thread`
  - `pt_spawn`
  - `pt_restart`
  - `pt_yield_until`
- 当前以显式 helper 风格作为 Uya 端口定稿语义

### C. `lc-switch` 端口语义
- 当前 `Lc` 已提供 `lc_init/lc_set/lc_resume/lc_end` 的显式状态版等价接口，并作为端口定稿语义

### D. `uip.c` 端口语义覆盖
- 已完成并有独立测试覆盖的重点包括：
  - TCP/UDP 主路径
  - ACK / NEWDATA / CLOSE / ABORT / CONNECTED
  - RST / FIN / ACK 优先级
  - `ack_outstanding`
  - timer / rexmit / timeout / TIME_WAIT
- IPv4 fragmentation/reassembly 已覆盖：
  - duplicate
  - overlap
  - timeout
  - 多片 bitmap
  - “未过期 partial datagram 不被新 identity 抢占”
  - `uip_reass_overflow(offset + payload_len)` 语义
- 完成重组后的输出模型已推进到复制整包到 `out`，并已有 `ports/uip/tests/uip_reass_output_test.uya` 作为输出路径测试入口
- 当前端口实现以现有拆分测试矩阵定义行为边界

### E. `uip-fw` / `uip-split` 的完整设备级行为未补齐
- `uip-fw`：广播路径、ICMP time exceeded 构造、与真实网卡输出回调的完整行为未完全复刻
- `uip-split`：与真实 `tcpip_output()`、`uip_appdata` 搬移和完整 checksum/分段发送路径的一致性仍是简化版

## 建议补齐顺序

建议按收益和实现风险排序：

1. `psock` 剩余事件驱动细节与应用层一致性
2. `uip_process()` 剩余 TCP 边界、statistics/logging/urgent 全路径
3. `pt/lc` 更接近原版的控制流层
4. `uip-fw` / `uip-split` 设备级细节
5. IPv6 路径（若项目范围需要）

## 已拆分测试

为避免 TCP 与 UDP 测试相互干扰，测试已按职责拆分：

- `ports/uip/tests/uip_core_base_test.uya`：基础类型、地址、校验和、定时器等核心能力（**已切到 `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`**)
- `ports/uip/tests/state_and_timer_test.uya`：状态初始化、监听、连接分配、UDP 连接管理与 `uip_init()` 对 UDP remote endpoint/TTL 清零（**已切到 `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`**)
- `ports/uip/tests/uip_tcp_core_test.uya`：TCP 核心处理逻辑（含 `UIP_UDP_TIMER` poll 路径边界）
- `ports/uip/tests/uip_tcp_core_edge_test.uya`：TCP 关闭尾声状态链等剩余边界小测试
- `ports/uip/tests/uip_tcp_core_ack_edge_test.uya`：established / syn_rcvd 上 ACK/appcall/app_slen/len 子集边界
- `ports/uip/tests/uip_tcp_psock_bridge_test.uya`：拆分出的 TCP→psock bridge 小测试（用于承载 `psock_event_from_process_result` / `psock_apply_event` / `psock_*_from_event` 组合，规避大测试文件工具链稳定性问题；含 connected 判定与 blocked-close/rexmit 保持回归）
- `ports/uip/tests/uip_tcp_handshake_test.uya`：TCP 握手与状态迁移
- `ports/uip/tests/udp_test.uya`：UDP 收发、路由逻辑与 miss/reset current selection 边界
- `ports/uip/tests/uip_arp_test.uya`：ARP 相关行为
- `ports/uip/tests/uiplib_ipaddrconv_test.uya`：`uiplib_ipaddrconv` 聚焦测试
- `ports/uip/tests/core_primitives_test.uya`：部分基础原语测试
- `ports/uip/tests/uip_neighbor_test.uya`：邻居表初始化、老化、更新、查找与替换策略（**已切到 `ports/uip/uip_base.uya` + `ports/uip/uip_neighbor_lib.uya` + `ports/uip/uip_ipv6_neighbor_glue.uya` + `ports/uip/uip_core.uya`**)
- `ports/uip/tests/uip_fw_test.uya`：转发接口选择、默认路由、TTL 递减、TTL expiry→ICMP time exceeded 与去重缓存
- `ports/uip/tests/uip_split_test.uya`：满尺寸 TCP 报文拆分发送、second-half appdata 搬移与 second-segment sequence 递增
- `ports/uip/tests/lc_test.uya`：local continuation 最小状态层
- `ports/uip/tests/pt_test.uya`：显式 resume-point/helper 风格的 protothread 模板与迁移用例（含 `pt_spawn()` child 初始化/clearing 回归）
- `ports/uip/tests/pt_migration_demo_test.uya`：独立的 protothread helper-style migration demo（send-ack / readto-chunk adapter）
- `ports/uip/tests/psock_test.uya`：protosocket 初始化、发送、读缓冲与读到标记
- `ports/uip/tests/psock_bridge_edge_test.uya`：psock 事件桥接、close/timed_out/aborted/ack/poll/rexmit/connected + newdata/readto 边界小测试（含 current-event view 与 delimiter 完成条件回归）
- `ports/uip/tests/uip_runtime_features_test.uya`：runtime/log/stats/urg/UDP checksum error/IPv6 invalid ND 相关小功能
- `ports/uip/tests/uip_urg_runtime_test.uya`：从 runtime features 中拆出的 urgent/logging/TCP 主流程联动小测试
- `ports/uip/tests/uip_timer_runtime_test.uya`：from runtime features 中拆出的 timer timeout/log/stats 小测试
- `ports/uip/tests/uip_stats_logging_test.uya`：从 runtime features 中拆出的 stats/logging 小测试
- `ports/uip/tests/uip_reass_test.uya`：fragment duplicate/overlap/timeout/bitmap 等关键语义
- `ports/uip/tests/uip_reass_output_test.uya`：fragment 完成重组后的输出模型与 IHL-sensitive payload 读取测试

## 测试入口矩阵

当前测试应按**模块归属**选择编译入口：

### 已切到拆分模块的测试
- `ports/uip/tests/lc_test.uya` → `ports/uip/uip_proto.uya`
- `ports/uip/tests/pt_test.uya` → `ports/uip/uip_proto.uya`
- `ports/uip/tests/pt_migration_demo_test.uya` → `ports/uip/uip_proto.uya`
- `ports/uip/tests/psock_test.uya` → `ports/uip/uip_proto.uya`
- `ports/uip/tests/psock_bridge_edge_test.uya` → `ports/uip/uip_proto.uya`
- `ports/uip/tests/uip_arp_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_arp.uya`
- `ports/uip/tests/uip_fw_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_fw_core.uya`
- `ports/uip/tests/uip_neighbor_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_neighbor_lib.uya` + `ports/uip/uip_ipv6_neighbor_glue.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_split_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_fw_core.uya`
- `ports/uip/tests/uip_runtime_features_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_urg_runtime_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_timer_runtime_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_stats_logging_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_reass_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_reass_output_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uip_ipv6_basic_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/core_primitives_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/uiplib_ipaddrconv_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya`
- `ports/uip/tests/state_and_timer_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`
- `ports/uip/tests/uip_core_base_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`
- `ports/uip/tests/udp_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`
- `ports/uip/tests/uip_tcp_core_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya` + `ports/uip/uip_arp.uya`
- `ports/uip/tests/uip_tcp_core_edge_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya` + `ports/uip/uip_arp.uya`
- `ports/uip/tests/uip_tcp_core_ack_edge_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya` + `ports/uip/uip_arp.uya`
- `ports/uip/tests/uip_tcp_psock_bridge_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya` + `ports/uip/uip_arp.uya`（当前在工具链类型检查阶段仍可能触发 segfault，保留为继续拆分目标）
- `ports/uip/tests/uip_tcp_handshake_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_proto.uya`
- `ports/uip/tests/uip_ipv6_neighbor_bridge_test.uya` / `ports/uip/tests/uip_ipv6_neighbor_glue_test.uya` → `ports/uip/uip_base.uya` + `ports/uip/uip_core.uya` + `ports/uip/uip_fw_core.uya`

### 当前 `uiplib.uya` 的角色
- `ports/uip/uiplib.uya` 已降级为轻量兼容入口，不再承载主实现
- 公共基础定义已收敛到 `ports/uip/uip_base.uya`
- 当前 `ports/uip/tests/*.uya` 已全部具备更小的模块化测试入口，不再要求统一依赖 `uiplib.uya`

## protothread 显式迁移模板

当前 `ports/uip/uip_proto.uya` 不再依赖原版 C 宏式 `PT_BEGIN/PT_END/PT_WAIT_THREAD/PT_SPAWN` 控制流，而是推荐使用显式 helper 组合：

- `pt_resume(pt)`：读取当前 continuation / resume point
- `pt_set_resume(pt, line)`：设置 resume point
- `pt_clear_resume(pt)`：清空 resume point
- `pt_wait_at(pt, line, cond)`：在显式 resume point 上等待条件
- `pt_wait_thread_at(pt, line, child_status)`：等待 child protothread 完成
- `pt_spawn_at(pt, child, line, child_status)`：启动并等待 child protothread
- `pt_end(pt)` / `pt_exit(pt)` / `pt_restart(pt)`：显式结束、退出或重启

推荐迁移形态：

1. `wait → wait`
2. `wait → spawn child → finish`
3. `ready → send child → ack`
4. `newdata → read child → line_done`
5. `readbuf → continue until drained`
6. `readto → continue across chunks until delimiter`
7. `ready/child → interrupt(close/abort/timeout) → early end`

可直接参考：
- `ports/uip/tests/pt_test.uya:1`

其中已包含这些 demo：
- `demo_pt_wait_two_steps_with_helper`
- `demo_psock_send_template`
- `demo_parent_two_stage_with_child`
- `demo_realistic_psock_sender`
- `demo_realistic_psock_reader`
- `demo_realistic_psock_readbuf_loop`
- `demo_realistic_psock_readto_chunks`
- `demo_interruptible_psock_flow`

这些测试文件可作为将真实模块中的 protothread 风格逻辑改写为显式 resume-point/helper 风格时的模板。

## 运行方式

在仓库根目录执行：

```bash
# 推荐：按拆分模块运行更小的测试编译入口
./uya/bin/uya test ports/uip/tests/uip_runtime_features_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
# 从 runtime features 拆出的 urgent/logging/TCP 主流程联动小文件；当前可能仍受工具链类型检查阶段 segfault 影响
./uya/bin/uya test ports/uip/tests/uip_urg_runtime_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
# 从 runtime features 拆出的 timer timeout/log/stats 小文件；当前可能仍受工具链类型检查阶段 segfault 影响
./uya/bin/uya test ports/uip/tests/uip_timer_runtime_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
# 从 runtime features 拆出的 stats/logging 小文件；当前可能仍受工具链类型检查阶段 segfault 影响
./uya/bin/uya test ports/uip/tests/uip_stats_logging_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/uip_reass_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/uip_reass_output_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/uip_ipv6_basic_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/core_primitives_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/uiplib_ipaddrconv_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
./uya/bin/uya test ports/uip/tests/state_and_timer_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/uip_core_base_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/udp_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_core_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya ports/uip/uip_arp.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_core_edge_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya ports/uip/uip_arp.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_core_ack_edge_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya ports/uip/uip_arp.uya
# 继续拆分中的 bridge 小文件；当前可能仍受工具链类型检查阶段 segfault 影响
./uya/bin/uya test ports/uip/tests/uip_tcp_psock_bridge_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya ports/uip/uip_arp.uya
./uya/bin/uya test ports/uip/tests/uip_tcp_handshake_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/uip_arp_test.uya ports/uip/uip_base.uya ports/uip/uip_arp.uya
./uya/bin/uya test ports/uip/tests/uip_fw_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/uip_neighbor_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/uip_split_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/uip_ipv6_neighbor_bridge_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/uip_ipv6_neighbor_glue_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/lc_test.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/pt_test.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/pt_migration_demo_test.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/psock_test.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/psock_bridge_edge_test.uya ports/uip/uip_proto.uya
```

当前不再建议使用下面这种“所有 tests 一律用 `uiplib.uya`”的伪全量回归方式，因为仓库已进入拆分阶段，测试入口应与模块归属对应：

```bash
# 仅示意：按测试归属选择模块入口，不建议统一绑定 uiplib.uya
./uya/bin/uya test ports/uip/tests/lc_test.uya ports/uip/uip_proto.uya
./uya/bin/uya test ports/uip/tests/uip_arp_test.uya ports/uip/uip_base.uya ports/uip/uip_arp.uya
./uya/bin/uya test ports/uip/tests/uip_fw_test.uya ports/uip/uip_base.uya ports/uip/uip_fw_core.uya
./uya/bin/uya test ports/uip/tests/uip_reass_test.uya ports/uip/uip_base.uya ports/uip/uip_core.uya
```

## 移植范围说明

当前移植覆盖内容包括：

- uIP 常量、类型与运行时状态定义
- IPv4 地址辅助函数
- 字节序与校验和计算
- TCP 主状态机与大量报文构造/状态迁移逻辑
- UDP 连接匹配、输入输出处理
- ARP 状态与基本操作
- 邻居表 `uip-neighbor`
- 转发模块 `uip-fw`
- TCP 拆分发送 `uip-split`
- local continuation 等价层 `lc`
- protothread 显式 helper 迁移模型 `pt`
- protosocket 兼容实现 `psock`
- 定时器与连接初始化能力
- runtime / statistics / logging / urgent / reassembly 的测试导向实现

## 说明

- 当前 `pt` / `psock` / `lc` 不是对原始 C 宏控制流的逐字节直译，而是按 Uya 语言规则实现的显式等价层或兼容版本。
- `lc-switch.h` 在 Uya 中采用显式状态结构替代，而不是保留 C 宏 `switch/case` continuation 技巧。
- `README.md` 当前已按 `TODO.md` 与现有测试拆分结果同步到较新的功能状态；后续若继续推进语义对齐，应优先同步更新这两处文档。
- 目前按测试文件分别编译/执行，暂不做聚合编译。
- 若后续继续统一修复，可在现有拆分基础上逐个回归测试。
