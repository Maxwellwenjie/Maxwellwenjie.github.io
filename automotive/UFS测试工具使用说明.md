---
title: UFS 测试工具 ufsparam 使用说明
date: 2026-11-25
summary: ufsparam 工具用法详解：读取 UFS 固件版本、健康报告、JEDEC 健康描述符与温度，含 8155/8295 平台及 arm/x86 架构选型。
tags: UFS, ufsparam, QNX, 存储测试
---

## 介绍

ufsparam是一个用以检测ufs设备健康状态的二进制工具，可以在QNX/Linux/Android系统级别启用以下操作：

- 读取固件版本信息；
- 通过SCSI命令读取供应商专有健康报告；
- 根据JEDEC JESD220E读取设备健康描述符；
- 读取支持的模式页；
- 读取描述符、标志和属性；
- 使用UFS-BSG Linux驱动程序发送UPIU事务，目前，仅提供查询请求UPIU；

**ufsparm工具下载**：[ufsparm.zip](https://ae-wiki.leapmotor.com/%E5%B5%8C%E5%85%A5%E5%BC%8Fbsp%E7%BB%84/ufsparm.zip)

**注**：解压后，**7.0文件夹**对应的是8155平台，**7.1文件夹**对应的8295平台；  
**arm架构下选择**：ufsparm_arm_64bit, **x86架构选择** : ufsparm

## 用法

在QNX系统串口终端输入./ufsparm_arm_64bit --help  
串口输出该命令具体用法。如下所示：（本文档只挑选其中重要的进行讲解）

```none
Usage:
         fw_version <SCSI device>
                Print fw version from SCSI device.

         micron_health_report <SCSI device>
                Print heath report from SCSI device.

         jedec_health_descriptor <SCSI device>
                Print Jedec health descriptor.

          micron_temperature <SCSI device>
                Print temperature report from SCSI device.
```


**设备路径**  
其中输入设备路径应该根据当前所运行的操作系统和驱动类型进行设置，具体如下所示：  
![[Pasted image 20260114092714.png]]

## 示例

**1.读取ufs固件版本信息命令：**

```none
# ./ufsparm_arm_64bit fw_version /dev/disk/uda1
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
Vendor identification: MICRON
Product identification: MT128GBCAV2U31AA
Product revision level: 0101
```


**输出参数详解：**

- _ufsparm v3.7_ ： 表示当前正在使用的ufsparm_arm_64bit工具版本是v3.7;
- _Device MICRON MT128GBCAV2U31AA 0101_ ： 芯片制造商是镁光，芯片型号是MT128GBCAV2U31AA,存储容量为128GB，0101为固件版本；
- _Vendor identification_ ： 设备生产商名称；
- _Product identification_ ： 设备确切产品型号；

**注**：上述命令是在8295平台上运行，对于8155平台有的设备可能不是镁光的，运行该命令会显示如下信息：

```none
# ./ufsparm_arm_64bit fw_version /dev/disk/uda0
ufsparm v3.7
Device: KIOXIA THGJFGT0T25BAZZA 0100

*** ufsparm is compatible with Micron UFS devices only ***
```


该输出信息提示该ufs设备的制造商是KIOXIA，产品型号为THGJFGT0T25BAZZA，且ufsparm_arm_64bit这个工具是专为镁光ufs设计的；

**2.读取镁光ufs芯片健康报告**

```none
# ./ufsparm_arm_64bit micron_health_report /dev/disk/uda0
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
  Factory bad blocks count  [0x00-0x01]:                     0x001A     (26)
  Run-time bad blocks count  [0x02-0x03]:                    0x0000     (0)
  Spare blocks count [0x04-0x05]:                            0x0007     (7)
  Exhausted life for Normal [0x0B]:                          0x02       (2%)
  Meta data corruption [0x0C-0x0D]:                          0x0000     (No Meta Data Corruption)
  Minimum virtual block erase count for Normal [0x10-0x13]:  0x00000001 (1)
  Maximum virtual block erase count for Normal [0x14-0x17]:  0x00000025 (37)
  Average virtual block erase count for Normal [0x18-0x1B]:  0x00000023 (35)
  Initialization count (success) [0x30-0x33]:                0x000001F3 (499)
  Initialization count (failure) [0x34-0x37]:                0x00001784 (6020)
  Read reclaim count for Normal [0x3C-0x3F]:                 0x00000000 (0)
  Read data size for Normal (unit: 100MB) [0x40-0x43]:       0x000101AB (65963)
  Written data size for Normal (unit: 100MB) [0x44-0x47]:    0x000076D0 (30416)
  SPOR write fail count [0x48-0x4B]:                         0x00000040 (64)
  SPOR recovery count [0x4C-0x4F]:                           0x00001784 (6020)
  VDET count [0x50-0x53]:                                    0x00000000 (0)
  UECC count [0x54-0x57]:                                    0x00000000 (0)
  Read retry count [0x58-0x5B]:                              0x000013B8 (5048)
  Temperature information [0x5C-0x5F]:                       0xC2697E70 (114 C, 25 C, 46 C, 32 C)
  Exhausted life for EM1 [0x62]:                             0x01       (1%)
  Read data size for EM1 (unit: 100MB) [0x68-0x6B]:          0x00000000 (0)
  Written data size for EM1 (unit: 100MB) [0x6C-0x6F]:       0x00000000 (0)
  Minimum virtual block erase count for EM1 [0x70-0x7E]:     0x00000001 (1)
  Maximum virtual block erase count for EM1 [0x74-0x77]:     0x0000011C (284)
  Average virtual block erase count for EM1 [0x78-0x7B]:     0x00000102 (258)
  Read reclaim count for EM1 [0x7C-0x7F]:                    0x00000000 (0)
  Erase amplification for Normal [0x80-0x81]:                0x0097     (1.51)
  Erase amplification for EM1 [0x82-0x83]:                   0x00FF     (2.55)
  Device-On Time [0x84-0x87]:                                0x00000533 (1331)
  UIC Error count [0x90-0x93]:                               0x00000066 (102)
  SER DED Count [0x94-0x97]:                                 0x00000000 (0)
  SEC Count [0x98-0x9B]:                                     0x00000000 (0)
  Urgent GC Count for Normal [0xA0-0xA3]:                    0x00000000 (0)
  Urgent GC Count for EM1 [0xA4-0xA7]:                       0x00000000 (0)
  Valid Page Percentage for Normal [0xA8-0xAB]:              0x00000017 (23%)
  Valid Page Percentage for EM1 [0xAC-0xAF]:                 0x00000027 (39%)
  RTBB [0xB0-0xB1]:                                          0x0000     (0)
  RTBB_SLC [0xB2-0xB3]:                                      0x0000     (0)
  Program_RTB [0xB6-0xB7]:                                   0x0000     (0)
  Erase_RTBB [0xB8-0xB9]:                                    0x0000     (0)
  Low Voltage Detection VCCQ [0xC0-0xC3]:                    0x00000000 (0)
  Low Voltage Detection VCC [0xC4-0xC7]:                     0x00000000 (0)
  Vccq Suddenly Power Off Count [0xC8-0xCB]:                 0x000008D8 (2264)
  Vcc Suddenly Power Off Count [0xCC-0xCF]:                  0x000008D8 (2264)
  Vccq Suddenly Power Off recovery count [0xD0-0xD3]:        0x0000076A (1898)
  Vcc Suddenly Power Off recovery count [0xD4-0xD7]:         0x0000076A (1898)
  Init Count [0xE0-0xE3]:                                    0x00001977 (6519)
  Current temperature [0xE4]:                                0x7E       (46 C)
  Available SLC cache (WB buffer) size [0xE8-0xEB]:          0x0000000A (10)
  Max SLC cache (WB) size [0xEC-0xEF]:                       0x00000BEA (3050)
  Patch Trial Count [0xF0-0xF1]:                             0x0000     (0)
  Patch Success Count [0xF2-0xF3]:                           0x0000     (0)
  Safe Shutdown & Initialization Count [0xF8-0xFB]:          0x000001F3 (499)
  Unsafe Shutdown & Initialization Count [0xFC-0xFF]:        0x000008D8 (2264)
```


**输出参数详解:**

- _Factory bad blocks count_ ： **出厂坏块数量**26个，属于正常现象；
- _run-time bad blocks count_ : **运行时坏块数量**；
- _pare blocks count_ : **剩余可用备用块数量**，用于在未来替换新产生的运行时坏块；
- _Ehausted life for Normal_ : ufs芯片的闪存颗粒磨损程序；
- _Meta data corruption_ : 元数据是否损坏，类似于分区表；
- _Minimum virtual block erase count for Normal_ : 最小擦除次数；
- _Maximum virtual block erase count for Normal_ : 最大擦除次数；
- _Initialization count (success)_ : 初始化成功次数；
- _Initialization count (failure)_ : 初始化失败次数（每次意外断电，如强制重启、系统死机重启等都会导致该次数增加）；
- _Read reclaim count for Normal_ : 读取刷新操作次数，**步骤为搬迁数据 -> 擦除旧块 -> 计数增加**；
- _Read data size for Normal (unit: 100MB)_ : 读取数据量，MB为单位；
- _Written data size for Normal (unit: 100MB)_ : 写入数据量，MB为单位；
- _SPOR write fail count_ : 当设备突然断电时，ufs控制器未能成功完成数据写入操作的次数；
- _SPOR recovery count_ : 意外断电恢复次数；
- _VDET count_ : 电压异常次数，记录UFS存储芯片的供电电压意外下降到预设危险阈值以下的次数；
- _UECC count_ : 不可纠正ECC错误，0表示没有发生过导致数据永久丢失的严重读写错误；
- _Read retry count_ : 读取重试次数；
- _Temperature information_ : 温度信息；
- _Exhausted life for EM1_ : EM1分区磨损程度；
- _Device-On Time_ : ufs上电总计工作时长；
- _UIC Error count_ : (ufs interconnect) 应该是CPU与ufs之间的硬件接口通信协议，当错误发生时，触发重试机制重新发送数据；
- _SER DED Count_ : (symbol error rate) ufs芯片自身在其高速串行接收端检测到的符号错误的累计计数；
- _SEC Count_ : (soft error correction) ufs成功纠正的可纠正错误累计次数；
- _Urgent GC Count for Normal_ ： 在主存储区域，ufs控制器被迫执行紧急垃圾回收操作的总次数；
- _Urgent GC Count for EM1_ : 在EM1区域，ufs控制器被迫执行紧急垃圾回收操作的总次数；
- _Valid Page Percentage for Normal_ : 在主存储区域的所有已使用的页中，**有效数据页所占的比例**；
- _Valid Page Percentage for EM_ : 在EM1区域的所有已使用的页中，**有效数据页所占的比例**；
- _RTBB_ : (run time Bad block) ufs在整个使用周期内，**新产生的、不可用的物理坏块总数量**；
- _RTBB_SLC_ : SLC模式下ufs在整个使用周期内，新产生的、不可用的物理坏块总数量；
- _Program_RTB_ : 在编程（写入）操作过程中产生的运行时坏块数量；
- _Erase_RTBB_ : 在擦除操作过程中产生的**运行时坏块数量**；
- _Low Voltage Detection VCCQ_ : VCQQ（1.2V或1.8V）低电压检测次数；
- _Low Voltage Detection VCC_ ：VCC（2.5V或3.3V）低电压检测次数；
- _Vccq Suddenly Power Off Count_ : Vccq电源突然断开次数；
- _Vcc Suddenly Power Off Count_ : Vcc电源突然断开次数；
- _Vccq Suddenly Power Off recovery count_ : 在Vccq电源突然断电后，成功恢复次数；
- _Vcc Suddenly Power Off recovery count_ : 在Vcc电源突然断电后，成功恢复次数；
- _Init Count_ : 设备初始化总次数；
- _Current temperature_ : 芯片当前温度；
- _Available SLC cache_ : 当前SLC缓存大小；
- _Max SLC cache (WB) size_ : SLC缓存的最大可配置大小；
- _Patch Trial Count_ : 固件修补尝试次数；
- _Patch Success Count_ : 固件修补成功次数；
- _Safe Shutdown & Initialization Count_ ： 安全关机及初始化次数，记录正常关机后成功启动的次数；
- _Unsafe Shutdown & Initialization Count_ : 不安全关机及初始化次数，记录非正常关机后控制器执行恢复流程并成功启动的次数；

**3.读取jedec 模式页**  
所谓JEDEC就是为整个微电子行业指定开放、公平的技术标准，确保不同厂商生产同类产品可以互相替换和协作；

```none
# ./ufsparm_arm_64bit  jedec_health_descriptor /dev/disk/uda0
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
Health Descriptor:
bLength: 0x2d
bDescriptorIDN: 0x09
bPreEOLInfo: 0x01
bDeviceLifeTimeEstA: 0x01
bDeviceLifeTimeEstB: 0x01
VendorPropInfo[0]: 0x27
VendorPropInfo[1]: 0x24
VendorPropInfo[2]: 0x01
VendorPropInfo[3]: 0x02
VendorPropInfo[4]: 0x01
VendorPropInfo[5]: 0x00
VendorPropInfo[6]: 0x00
VendorPropInfo[7]: 0xc2
VendorPropInfo[8]: 0x69
VendorPropInfo[9]: 0x96
VendorPropInfo[10]: 0x6f
VendorPropInfo[11]: 0x00
VendorPropInfo[12]: 0x00
VendorPropInfo[13]: 0x00
VendorPropInfo[14]: 0x00
VendorPropInfo[15]: 0x00
VendorPropInfo[16]: 0x00
VendorPropInfo[17]: 0x76
VendorPropInfo[18]: 0xef
VendorPropInfo[19]: 0x00
VendorPropInfo[20]: 0x00
VendorPropInfo[21]: 0x00
VendorPropInfo[22]: 0x00
VendorPropInfo[23]: 0x00
VendorPropInfo[24]: 0x01
VendorPropInfo[25]: 0x01
VendorPropInfo[26]: 0xed
VendorPropInfo[27]: 0x00
VendorPropInfo[28]: 0x00
VendorPropInfo[29]: 0x00
VendorPropInfo[30]: 0x00
VendorPropInfo[31]: 0x02
```

**输出参数解析**：

- _bLength_ ： 描述符总长度；
- _bDescriptorIDN_ ： 描述符标识符，0x09固定表示这是一个Health描述符；
- _bPreEOLInfo_ ： (pre-End of life information)寿命终止前信息，指示设备预计剩余寿命状态，**0x01 : 正常， 0x02 : 警告， 0x03 : 危险**；
- bDeviceLifeTimeEstA ： **设备寿命估计值**。0x00 = 0% - 10%寿命已用，0x01 = 10% - 20%寿命已用， ... 0x0A = 100% 寿命已耗尽；
- _VendorPropInfo[x]_ : 厂商自定义字段；

**4.更新ufs固件**

```none
./ufsparm_arm_64bit ffu <SCSI device> <FFU binary>
```


**5.读取ufs温度**

```none
# ./ufsparm_arm_64bit micron_temperature /dev/disk/uda7
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
NAND 1 temperature: 49 C
NAND 2 temperature: 49 C
```


**6.检查逻辑分区状态**

```none
./ufsparm_arm_64bit micron_lba_status <SCSI device> <LUN> <LBA_start> <LBA_count> [print_option=0]

Print_option:
Unmapped (0): print unmapped LBAs from LBA_start to LBA_count-1
Unmapped (1): print mapped LBAs from LBA_start to LBA_count-1
Compact (2): print ranges of consecutive mapped and unmapped LBAs

#用法
# ./ufsparm_arm_64bit check_lba_status /dev/block/sda 0 0 100 0
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
LBA start: 0
LBA count: 100
Unmapped LBAs: 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41
42 43 44 45 46 47 48 49 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76 77 78
79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99
Number of unmapped LBAs: 70
```


**输出参数解析**

- LBA start ： 逻辑块地址起始；
- LBA count ： 逻辑块地址数量；
- Unmapped LBAs ： 未映射逻辑块地址；
- Number of unmapped LBAs : 未映射逻辑块地址数量；

```none
#mapped only
# ./ufsparm_arm_64bit check_lba_status /dev/block/sda 0 0 100 1
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
LBA start: 0
LBA count: 100
Mapped LBAs: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 50 51 52 53 54 55
56 57 58 59
Number of mapped LBAs: 30

#compact
# ./ufsparm_arm_64bit check_lba_status /dev/block/sda 0 0 100 2
ufsparm v3.7
Device: MICRON MT128GBCAV2U31AA 0101
LBA start: 0
LBA count: 100
LBA 0-19: mapped
LBA 20-49: unmapped
LBA 50-59: mapped
LBA 60-99: unmapped
```


**注**：Unmapped LBA:意味着没有为这个LBA分配任何物理存储空间。当尝试读取一个unmapped的LBA时，控制器会直接返回全零数据，而不会访问任何闪存颗粒。当尝试写一个unmapped LBA时，控制器会为其分配一个空闲物理页，建立映射关系，然后将数据写入，此后，该LBA变为mapped状态。