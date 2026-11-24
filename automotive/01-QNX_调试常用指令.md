## 平台类

### qnx端查看版本号

cat /mnt/etc/issue

### 查看命令用法-Use

示例：  
Use -a pidin ar

### 获取进程号

pidin | grep LpUnity

### 查看单核CPU占用率

hogs | grep LpUnity

实车查看:  
hogs -l 25  
hogs -l 25 | grep lpHMIUtils

### 查看多核CPU占用率

top

### 查看显存

showmem -t mm_dma

### 看线程名

pidin -p $(slay -p LpUnity) threads

### 看CPU在哪个核

pidin -p $(slay -p LpUnity) sched

### 查看CPU温度

cat /dev/thermalmgr

### 查看8155平台GPU

echo gpu_set_log_level 4 > /dev/kgsl-control  
echo gpubusystats 1000 > /dev/kgsl-control  
slog2info -w |grep measurement

### 查看8295平台GPU

echo gpu_set_log_level 4 > /dev/kgsl-control  
echo gpubusystats 1000 > /dev/kgsl-control  
slog2info -w |grep utilization

### 查看log日志各节点

cd /dev/shmem/slogger2

### 显示驱动节点

cat /dev/dis

结果  
disk/  
display_ivimd_dp  
displaylog1  
display_icu_ivisd  
displaylog0

### 动态更新文本文件

tail -f xxx.log

### 解压Tar压缩包

tar -xvf QnxBuild.tar

### 压缩包

tar -cvf **.tar **/

### 追加文本内容到文件中

echo "\ncd /opt/data/\nsh check_alive.sh &\n" >> /mnt/scripts/startup.sh  
  

## 应用类

  

### 启动Unity

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/usr/lib64/:/lib64/:/lib/:/opt/data/icu/test/

### 设置环境变量方式

export SDL_VIDEO_EGL_DRIVER=libESXEGL_Adreno.so  
export SDL_VIDEO_GL_DRIVER=libESXGLESv2_Adreno.so

### 程序重定向

./LpUnity >/dev/slog2/stderr &

### 安卓保存日志

logcat -b all > /sdcard/logcat.txt

### 绑核心启动

on -R 0x0f /opt/data/icu/LpUnity/LpUnity &

### 切换到内网

export SOCK=/

### 板卡中挂载网络盘

export SOCK=/alt && fs-nfs3 10.192.126.230:/nfs/luo_fei2/mount/ /fei

### 亮屏指令 C23款：

i2cdbgr -a /dev/i2c3 -b 0x2d -z 0x00 192 0;  
i2cdbgr -a /dev/i2c1 -b 0x39 -z 0x00 192 0;  
i2cdbgr -a /dev/i2c1 -b 0x3c -z 0x00 192 0

### 其他

test_backlight -w 0 200

### 下线配置相关

#### 读取下线配置

/opt/usr/bin/pceTool -r hex f1a8

#### 写下线配置

/opt/usr/bin/pceTool -w hex f1a8 0  
新的命令：/opt/usr/bin/dcc -m lpDMApp -c w -s 1#EOL_CONFIG#hex#144#0

#### 清除所有铁电数据

/opt/usr/bin/dcc -m lpStoreService -c erase

### 清修改oem分区（例如/opt/usr/）

mount -o remount,rw /dev/disk/oem_a /opt/usr/  
oem_a B oem_b 8295

### 进后台

89456*5*89#  
新密码 5#93#2714*6809

### 进不来需要进安卓绑定一下

la  
am start com.leapmotor.phone/com.leapmotor.phone.activity.BackEndActivity

### 挂载网络小板

1. 设置ip  
    ifconfig [⽹卡] [172.17.4.xxx](http://172.17.4.xxx/) netmask 255.255.255.0
2. 建议先ping⼀下是否能ping通  
    ping 172.17.4.18
3. [...]表示文件层级不限 建议建⽴⼀个mnt文件夹⽤于挂载  
    例如  
    "fs-nfs3 172.17.4.18:/home/common/he_quanlin/mnt/8295 /he"  
    fs-nfs3 172.17.4.18:/home/common/[姓_名]/[...]/ /mnt  
    ifconfig emac0 172.17.4.98 netmask 255.255.255.0  
    ping 172.17.4.231  
    fs-nfs3 172.17.4.231:/home/common/luo_fei/ /luo

### HPC挂载

ftp地址：10.192.126.230 端口默认为：21  
账号密码：yibiao/Yibiao@lp123

1. 电脑上ftp上传需要的文件
2. 在板卡上输入ftp 10.192.126.230 输入账号密码
3. ls -l 查看有哪些文件； 下载ftp上面的文件：get 文件名 ； 上传板卡上面的文件： put 板卡上面的文件
4. exit或者bye退出ftp
5. 如果有ftpget和ftpput命令，也可以用下面命令  
    ftpget -u yibiao -p Yibiao@lp123 10.192.126.230 app.log app.log  
    ftpput -u yibiao -p Yibiao@lp123 10.192.126.230 app.log app.log  
    用法：Usage: ftpget [OPTIONS] HOST [LOCAL_FILE] REMOTE_FILE  
    用法：Usage: ftpput [OPTIONS] HOST [REMOTE_FILE] LOCAL_FILE

### FTP传输

ftp地址：10.192.126.230 端口默认为：21  
账号密码：yibiao/Yibiao@lp123

1. 电脑上ftp上传需要的文件
2. 在板卡上输入ftp 10.192.126.230 输入账号密码
3. ls -l 查看有哪些文件； 下载ftp上面的文件：get 文件名 ； 上传板卡上面的文件： put 板卡上面的文件；
4. exit或者bye退出ftp
5. 如果有ftpget和ftpput命令，也可以用下面命令：  
    ftpget -u yibiao -p Yibiao@lp123 10.192.126.230 app.log app.log  
    ftpput -u yibiao -p Yibiao@lp123 10.192.126.230 app.log app.log  
    用法：Usage: ftpget [OPTIONS] HOST [LOCAL_FILE] REMOTE_FILE  
    用法：Usage: ftpput [OPTIONS] HOST [REMOTE_FILE] LOCAL_FILE

### QNX截屏 QNX screenshot命令

截取屏幕内容输出为图片。  
语法：  
screenshot [-display=display_id]  
[-file=output_file]  
[-size=widthxheight]  
选项：  
-display=display_id  
设置要抓取的display id或连接类型，如果输入整型数字，那么自动认为是display id，如果输入是字符串，自动认为要截取相应连接类型的内容。支持的连接内容为：internal，composite，svideo，YPbPr，rgb，rgbhv，dvi，hdmi。  
-file=output_file  
指定输出路径，默认为screenshot.bmp。  
-size=widthxheight  
指定屏幕大小，默认全屏。

### EE3.5平台开启DDS服务

export DISCOVERY_SERVER_IPADDRESS=192.168.1.1  
./run_DiscoveryServer.sh 8295_qnx /opt/data/icu/test/fast-discovery-server

### 板子上挂载共享目录

export SOCK=/alt && fs-nfs3 10.192.126.230:/nfs/luo_fei2/mount/ /fei

### Unity日志路径

cat /opt/usr/bin/QnxBuild/Unknown Vendor/Unknown Unity Application/Player.log

### 刷高德码

/opt/usr/bin/pceTool -w str f1b1 LPSDK202103250000000000000000202Y7ZDDWWN7FKWK2CL4LG7PRESMWJY7ACBJHR4XRXWJ3JDSKQN

  

## 安卓类

  

### 安卓调试界面升级系统

1. 连接串口线
2. 长按电话按钮 打开拨号界面 输入： 89456*5*89#
3. 切换串口  
    switch Device
4. 在Win打开CMD
5. 输入  
    adb shell
6. 创建文件夹  
    /data/media/10/Documents/update
7. 退回CMD界面  
    exit
8. 上传系统包  
    adb push D:\lf\SoftPack\Update\LP-ICHS030-AA_V1.13.06_R_20221229.swu /data/media/10/Documents/update
9. 拷贝结束后,进入中控调试界面 点刷新C11 选择系统文件 点击升级

### 开启安卓FTP

1. 将ftpandroid程序拷贝到安卓系统中 data下  
    获取root权限： adb root  
    将程序包adb push 到/data/ftp/： adb push D:\0Code\LP_B11_ICU_Unity3D\ICU\8295\Release\Display.tar /data/ftp/  
    adb pull /data/ftp/ f:\Camera  
    进入到安卓系统的/data/ftp文件加，开启FTP服务： ./ftpandroid  
    进入QNX系统中，连接ftp 192.168.1.3 用户名:admin 密码123456  
    ftp -P 2121 192.168.1.3  
    get下载数据

### 修改安卓访问内网白名单

adb root  
adb remount 修改将 '/system' 部分置于可写入的模式，默认情况下 '/system' 部分是只读模式的。这个命令只适用于已被 root 的设备。  
adb pull /vendor/etc/lp_private_network_white_list.xml D:/

#### 添加应用名称

adb push D:/lp_private_network_white_list.xml /vendor/etc/

#### 修改安卓分屏白名单 adb root

adb remount  
adb pull /vendor/etc/lp_recent_task_black_list.xml

#### 拉取预置名单

![alt text](https://ae-wiki.leapmotor.com/zh/%E5%B5%8C%E5%85%A5%E5%BC%8FHMI%E7%BB%84/%E6%95%99%E7%A8%8B/image.png)  
adb push lp_recent_task_black_list.xml /vendor/etc/

#### 然后名单放回去

adb shell sync  
adb reboot

#### 然后重启

#### 设置分屏开关

adb shell settings put global strCarSplitScreen 1

### 安卓录屏

adb shell screenrecord /sdcard/demo.mp4  
按Ctrl+C键盘可停止屏幕录制，  
adb pull /sdcard/demo.mp4  
指定视频分辨率大小，参数 --size  
adb shell screenrecord --size 1280*720 /sdcard/demo.mp4  
截屏  
adb shell screencap -p /sdcard/screenshot.png

### 设置CAN通道白名单

sed -i 's/"can_chn": ([0-9]|[0-9][0-9])/"can_chn":5/g' filter*.json  
mkdir -p /opt/data/icu/filter_bak/  
mv /opt/usr/bin/filter* /opt/data/icu/filter_bak/  
chmod 777 /opt/data/icu/filter_bak/*  
sed -i 's/"can_chn": 1/"can_chn": 5/g' /opt/data/icu/filter_bak/filter*.json  
cp -f /opt/data/icu/filter_bak/* /opt/usr/bin/  
sync

### 修改启动脚本（例如/scripts）

mount -o remount,rw /dev/disk/system_a /  
system_a B system_b 8295  
修改oem分区（例如/opt/usr/） : mount -o remount,rw /dev/disk/oem_a /opt/usr/  
修改启动脚本（例如/mnt/scripts） mount -o remount,rw /dev/disk/system_a /mnt

### [¶](https://ae-wiki.leapmotor.com/zh/%E5%B5%8C%E5%85%A5%E5%BC%8FHMI%E7%BB%84/%E6%95%99%E7%A8%8B/Qnx%E5%B9%B3%E5%8F%B0%E8%B0%83%E8%AF%95%E5%B8%B8%E7%94%A8%E6%8C%87%E4%BB%A4#lphmi%E5%91%BD%E4%BB%A4%E5%8F%82%E6%95%B0-11104%E4%B8%BA%E4%BF%A1%E5%8F%B7id)lpHmi命令参数 11104为信号ID

./dcc -m lpHmi -c cansignal -s 11104