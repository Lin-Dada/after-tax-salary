# 应纳所得税额 = 税前工资 - 各项社会保险费 - 起征点 - 专项扣除费
# 应纳税额 = 应纳所得税额 * 税率 - 速算扣除数
# 税后工资 = 税前工资 - 各项社会保险费 - 应纳税额

base = float(input("请输入你的base工资 元/月 （不含房补等）："))
other_bonus = float(input("请输入你的各种补贴总计 元/月："))
gjj_ratio = float(input("请输入你的公积金缴纳比例 (0 ~ 0.12之间)："))
nianzhong = float(input("请输入你预计能拿多少个月年终奖 ："))
nianzhong_mon = int(input("请输入你们公司发年终奖的月份 （1~12之间）："))
city = input("请输入你的城市 （目前只支持gz、sz、hz、cq）：")
nianzhong *= base

last_yingna = 0.0 # 上个月累计已扣的税额
yingnasd = 0.0 # 当前累计应纳所得税额

def cacl_shebao_and_gongjijin(base, city):
    # 广州
    # 养老保险最高基数为22941，缴纳比例是8%
    # 医疗保险最高基数为33786，缴纳比例是2%
    # 失业保险最高基数为33786，缴纳比例是0.2%

    # 杭州
    # 养老保险最高基数为19783，缴纳比例是8%
    # 医疗保险最高基数为19783，缴纳比例是2%
    # 失业保险最高基数为19783，缴纳比例是0.5%

    # 深圳
    # 养老保险最高基数为22941，缴纳比例是8%
    # 医疗保险最高基数为34860，缴纳比例是2%
    # 失业保险最高基数为2360，缴纳比例是0.3%

    # 重庆
    # 养老保险最高基数为17455，缴纳比例是8%
    # 医疗保险最高基数为17455，缴纳比例是2%
    # 失业保险最高基数为17455，缴纳比例是0.5%
    if city == "gz":
        baoxian = min(22941, base) * 0.08 + min(33786, base) * 0.02 + min(33786, base) * 0.002
    elif city == "hz":
        baoxian = min(19783, base) * 0.08 + min(19783, base) * 0.02 + min(19783, base) * 0.005
    elif city == "sz":
        baoxian = min(22941, base) * 0.08 + min(34860, base) * 0.02 + min(2360, base) * 0.003
    elif city == "cq":
        baoxian = min(17455, base) * 0.08 + min(17455, base) * 0.02 + min(17455, base) * 0.005
    else:
        print("不支持的城市！目前只支持广州、杭州、深圳、重庆")
        exit(-1)
    gongjijin = base * gjj_ratio
    return baoxian, gongjijin

# 返回当前税率及速算扣除数
def get_ratio(yingnasd):
    if yingnasd < 0 :
        print("请检查你的输入！")
        exit(-1)
    if yingnasd <= 36000: return 0.03, 0.0
    if yingnasd <= 144000: return 0.1, 2520.0
    if yingnasd <= 300000: return 0.2, 16920.0
    if yingnasd <= 420000: return 0.25, 31920.0
    if yingnasd <= 660000: return 0.30, 52920.0
    if yingnasd <= 960000: return 0.35, 85920.0
    return 0.45, 181920.0

sum = 0
_, gjj = cacl_shebao_and_gongjijin(base, city)
gjj *= 2 * 12
baoxian, gongjijin = cacl_shebao_and_gongjijin(base, city)

print("\n每个月固定扣除社保 {:.2f} 元，扣除公积金 {:.2f} 元".format(baoxian, gongjijin))

for i in range(12):
    # shebao_and_gongjijin：社保和公积金

    if nianzhong_mon == i + 1:
        all_money = base + other_bonus + nianzhong
    else:
        all_money = base + other_bonus
        # yingnasd: 累计应纳所得税额
    yingnasd += all_money - baoxian - gongjijin - 5000
    # 税率、速算扣除数
    ratio, susuan = get_ratio(yingnasd)
    # yingna: 应纳税额
    yingna = yingnasd * ratio - susuan - last_yingna
    last_yingna += yingna
    # shuihou：税后工资
    shuihou = all_money - baoxian - gongjijin - yingna
    sum += shuihou
    if nianzhong_mon == i + 1:
        print("【发年终】第 {} 个月税前收入{:.2f} 元（含补贴），扣税 {:.2f} 元，扣除五险一金和个税后总计到手：{:.2f} 元".format(i+1, all_money, yingna, shuihou))
    else:
        print("第 {} 个月税前收入{:.2f} 元（含补贴），扣税 {:.2f} 元，扣除五险一金和个税后总计到手：{:.2f} 元".format(i + 1, all_money, yingna,
                                                                                         shuihou))
print("\n税后总收入：{:.2f} 元，累计公积金为{:.2f} 元".format(sum, gjj))

