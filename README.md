# uIP-uya

一个使用 **uya** 重写 **C 语言版 uIP 协议栈** 的实验性项目。

本项目只做一件事：

> **严格按照 C 版 uIP 的已有功能进行移植，不做协议能力扩展，不改造成新的网络栈。**

---

## 项目目标

uIP-uya 的目标是：

1. 用 uya 重写 C 版 uIP，而不是设计一套新的协议栈架构。
2. 保留 uIP 的单主缓冲区、固定容量表、编译期裁剪、ARP 外接处理等原始设计。
3. 让实现过程可以通过 host-side 测试逐步验证。
4. 保持文档、代码、测试三者一致。

本项目当前不以“功能扩展”为目标，只以“**移植 C 版 uIP 既有能力**”为目标。

---

## 设计原则

### 1. 忠实移植，而不是重新架构

本项目的目标不是借 uIP 之名设计一个“更现代”的协议栈，而是尽量保留 C 版 uIP 的核心设计，例如：

- `uip_buf + uip_len` 主缓冲区模型
- `uip_process(flag)` 单核入口
- 固定容量 TCP / UDP / ARP 状态表
- 驱动与协议栈直接协作的调用方式
- ARP 在核心之外独立处理

### 2. 静态资源模型

uya 版继续沿用 uIP 的资源模型：

- 静态分配
- 固定容量数组
- 单主缓冲区
- 避免动态扩容
- 不引入多 buffer 池

### 3. 可测试，但不改变核心行为模型

允许为了 host-side 回归测试加入辅助入口，但这些辅助入口不代表长期公共 API，也不能改变核心协议处理方式。

---

## 当前版本信息

- 项目版本：`uya-uip v0.1.0`
- 项目分支：`main`
- 当前提交：`4843f24`
- uya 版本：`v0.9.4`
- 最近验证时间：`2026-05-10`
- 编译状态：通过（`./uya/bin/uya test src/uip/uip_types_test.uya`）
- 当前测试基线：`50` 个测试中 `44` 个通过，`6` 个失败

---

## 当前代码状态

当前仓库已经不是纯文档或纯骨架状态，而是已经实现了 **C 版 uIP 的最小可运行子集**。

当前已完成的主要内容包括：

- `src/uip/uip_types/mod.uya`
  - 核心协议类型、头部结构、状态枚举、常量
- `src/uip/uip_conf/mod.uya`
  - 编译期配置常量
- `src/uip/uip_core/mod.uya`
  - 全局状态、初始化、核心入口、最小 TCP/UDP/IP/ICMP 路径
- `src/uip/uip_arp/mod.uya`
  - ARP 表、ARP 输入处理、ARP 老化、出站封装
- `src/uip/uip_arch/mod.uya`
  - 字节序与校验和辅助
- `src/uip/uip_types_test.uya`
  - 当前 host-side 回归测试集合

当前已具备的最小协议闭环包括：

- ARP cache / request / reply / aging
- 发往本机的 ICMP echo request → echo reply
- UDP 连接分配、最小入站匹配、周期发送、checksum 校验
- TCP 最小握手、最小收发、最小关闭、部分定时器与重传路径

当前**尚未声明完成完整 C 版 uIP 移植**。后续工作仍然是：

- 对照 `uip.c` / `uip.h` / `uip_arp.c` 补齐缺失功能
- 保持实现边界不超出原版
- 不新增超出原版的新能力

---

## 仓库结构

```text
src/
  uip/
    uip_arch/
      mod.uya
    uip_arp/
      mod.uya
    uip_conf/
      mod.uya
    uip_core/
      mod.uya
    uip_types/
      mod.uya
    uip_types_test.uya

docs/
  README.md
  architecture.md
  uip-porting-plan.md
  uip-roadmap.md
```

主要模块含义：

- `src/uip/uip_core/mod.uya`
  - 对应 C 版 `uip.c`
  - 承载全局状态、核心入口与当前主流程实现
- `src/uip/uip_types/mod.uya`
  - 对应 `uip.h` 中的主要类型、头部与状态定义
- `src/uip/uip_conf/mod.uya`
  - 对应 `uipopt.h` / `uip-conf.h` 风格的配置模型
- `src/uip/uip_arp/mod.uya`
  - 对应 `uip_arp.c`
  - 实现 Ethernet/ARP 外接处理逻辑
- `src/uip/uip_arch/mod.uya`
  - 对应 `uip_arch.h`
  - 提供字节序与校验和辅助能力
- `src/uip/uip_types_test.uya`
  - 当前回归测试集合

---

## 开发约束

后续实现必须继续遵循：

1. 优先补齐 C 版已有路径
2. 不新增协议能力
3. 不重构成新的网络栈架构
4. 不把测试辅助接口写成正式对外 API 承诺
5. 文档只描述当前代码已实现的内容，或明确列出尚未完成项

---

## 文档索引

建议按以下顺序阅读：

1. `README.md`
   - 项目定位、目标、当前状态总览
2. `docs/architecture.md`
   - 当前代码与 C 版 uIP 的结构映射
3. `docs/uip-porting-plan.md`
   - 按当前实现状态整理的迁移清单
4. `docs/progress.md`
   - 当前已实现 / 未实现 / 与 C 版对照结论
5. `docs/TODO.md`
   - 当前按 C 版功能补齐的待办清单
6. `docs/uip-roadmap.md`
   - 严格面向 C 版功能补齐的路线图

---

## 愿景

uIP-uya 的目标不是“做一个更现代的 uIP 替代品”，而是：

> **用 uya 把 C 语言版 uIP 重新实现一遍，并保持实现边界不超出原版。**
