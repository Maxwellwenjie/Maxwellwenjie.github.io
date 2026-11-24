---
title: 克隆 CAN 报文显示
date: 2026-11-24
summary: 介绍如何使用 ZCAN PRO 工具和 CAN 卡克隆 CAN 总线的报文显示，包含完整操作步骤与 DataID 配置说明。
tags: CAN, Clone
---

介绍如何使用ZCAN PRO工具和CAN卡克隆CAN总线的报文显示

# 1. 背景

在座舱开发新功能涉及到CAN报文发送时，需要确认CAN报文是否正确发送到CAN总线。目前经常用的方法主要是向CAN网关应用订阅对应的CAN通道报文。CAN网关收到发送的报文时，会输出到CAN网关日志。但是该方法不足之处是只能显示固定长度的数据，且显示都是十六进制数据，不是很直观。

VIU小组实现了通过CAN卡与ZAN PRO工具借用D-CAN实现发送报文的克隆显示。当前支持如下CAN报文的克隆显示。

```none
PCAN/BCAN/ACAN/CCAN/COMCAN/ETHCAN
```

# 2. 操作步骤

## 2.1. 关闭29认证

```sh
后台UDS诊断发0x723：2E018201
```


![[Pasted image 20260119163126.png]]

## 2.2. 开启克隆（以ETH-CAN为例）

```none
后台UDS诊断发0x723：31010206
```


![[Pasted image 20260119163132.png]]

支持的CAN对应的开启Command如下：

```none
0x723：31010202（PCAN）
0x723：31010201（BCAN）
0x723：31010207（ACAN）
0x723：3101020A（CCAN）
0x723：3101020E（COMCAN）
0x723：31010206（ETHCAN）
```


## 2.3. 发送会话保活报文

OBD口诊断CAN周期（小于5s）发0x7DF：023E80（会话保活）

> 注：步骤3需要在步骤2发送完成后，5s内开始发送。不然会会话超时，需要重新操作2、3步骤。

![[Pasted image 20260119163141.png]]

# 3. 结果查看

以ETH-CAN为例完成第1和2小节操作后，使用ZCAN PRO新建DBC视图，加载ETH-CAN的DBC文件，这时就可以实时查看发送的ETH-CAN的报文。

![[Pasted image 20260119163147.png]]

> 注意：每次设备重启后都需要重新设置。
