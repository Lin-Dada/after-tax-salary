# after-tax-salary
这是一个用于计算税后到手工资的程序，包含单机版和在线版本。单机版本直接可以本地运行，在线版本则可以部署在自己的服务器上作为Web Service。以下是所需的环境。

# 说明 
- 按照新税法进行计算，即把年终奖也算进梯度计税中。目前大部分计算器都不考虑这点，所以自己写了个程序实现。
- 补贴是指例如房补这种东西，会扣个税，但不扣社保。不是指餐补
- 目前只支持4个城市，可以自己在代码中增加对其他城市的支持，参考代码注释部分。

## 单机版（offline_version.py）
- python 3以上，我的是python 3.7
- `python offline_version.py` 启动

## 在线版（salary.py）
- python 3以上，我的是python 3.7
- flask(1.1.1)、flask_WTF(1.0.1)、flask_bootstrap(3.3.7.1)，版本应该不重要
  - `pip install flask`
  - `pip install flask_WTF`
  - `pip install flask_bootstrap`
- 在服务器端可以前台启动：
  - `python salary.py` 
- 也可以后台启动：
  - `nohup python salary.py > log 2>&1 &`，该命令把标准流输出重定向到log文件中
- 在线版界面截图（图中数据仅为测试，不代表真实工资）

![](/pics/1.png)
![](/pics/2.png)
