from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask import Flask, render_template, request, render_template_string
from flask_wtf.csrf import CSRFProtect
import os
import datetime

app = Flask(__name__)
#csrf = CSRFProtect(app)
app.secret_key = os.urandom(24)
bootstrap = Bootstrap(app)

# 计算社保和公积金，可网上查询基数和比例后在这里添加城市：https://www.findhro.com/22js1381.html
def cacl_shebao_and_gongjijin(base, city, gjj_ratio):
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
    city_cn = ""
    if city == "gz":
        city_cn = "广州"
        baoxian = min(22941, base) * 0.08 + min(33786, base) * 0.02 + min(33786, base) * 0.002
    elif city == "hz":
        city_cn = "杭州"
        baoxian = min(19783, base) * 0.08 + min(19783, base) * 0.02 + min(19783, base) * 0.005
    elif city == "sz":
        city_cn = "深圳"
        baoxian = min(22941, base) * 0.08 + min(34860, base) * 0.02 + min(2360, base) * 0.003
    elif city == "cq":
        city_cn = "重庆"
        baoxian = min(17455, base) * 0.08 + min(17455, base) * 0.02 + min(17455, base) * 0.005
    else:
        print("不支持的城市！目前只支持广州、杭州、深圳、重庆，你的输入：{}".format(city))
        return 0, 0, "", -1
    gongjijin = base * gjj_ratio
    return baoxian, gongjijin, city_cn, 0

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

class LoginForm(FlaskForm):
    base = StringField(u'请输入你的base工资 元/月 （不含房补等）：', validators=[
                DataRequired(message= u'此项不能为空'), Length(1, 64), ])
    other_bonus = StringField(u'请输入你的各种补贴总计 元/月：', validators=[
                DataRequired(message= u'此项不能为空'), Length(1, 64)])
    gjj_ratio = StringField(u'请输入你的公积金缴纳比例 (0 ~ 0.12之间)：', validators=[
        DataRequired(message=u'此项不能为空'), Length(1, 64)])
    nianzhong = StringField(u'请输入你预计能拿多少个月年终奖 ：', validators=[
        DataRequired(message=u'此项不能为空'), Length(1, 64)])
    nianzhong_mon = StringField(u'请输入你们公司发年终奖的月份 （1~12之间）：', validators=[
        DataRequired(message=u'此项不能为空'), Length(1, 64)])
    city = StringField(u'请输入你的城市，如sz （目前只支持gz、sz、hz、cq，即广州、深圳、杭州、重庆）：', validators=[
        DataRequired(message=u'此项不能为空'), Length(1, 64)])
    submit = SubmitField(u'点击计算我的到手收入！')

@app.route('/salary', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if request.method == "GET":
        return render_template('salary.html', form=form)
    else:
        try:
            base = float(form.base.data)
            other_bonus = float(form.other_bonus.data)
            gjj_ratio = float(form.gjj_ratio.data)
            nianzhong = float(form.nianzhong.data)
            nianzhong_mon = float(form.nianzhong_mon.data)
            city = form.city.data
        except:
            res = "<h4>请输入正确的数字！</h4>"
            return render_template('result.html', result=res)

        nianzhong *= base
        last_yingna = 0.0  # 上个月累计已扣的税额
        yingnasd = 0.0  # 当前累计应纳所得税额

        sum = 0
        baoxian, gongjijin, city_cn, err = cacl_shebao_and_gongjijin(base, city, gjj_ratio)
        if base < 0 or other_bonus < 0:
            res = "<h4>base或房补不能为负数</h4>"
            return render_template('result.html', result=res)
        if gjj_ratio < 0 or gjj_ratio > 0.12:
            res = "<h4>公积金缴纳比例应在0~0.12之间，你的输入：{}</h4>".format(gjj_ratio)
            return render_template('result.html', result=res)
        if nianzhong_mon < 0 or nianzhong_mon > 12:
            res = "<h4>年终奖发放月份应在1~12之间，你的输入：{}</h4>".format(nianzhong_mon)
            return render_template('result.html', result=res)
        if err == -1:
            res ="<h4>不支持的城市！目前只支持广州、杭州、深圳、重庆，你的输入：{}</h4>".format(city)
            return render_template('result.html', result=res)


        gjj = gongjijin * 12 * 2
        res = "月base：<b>{:.2f}</b> 元，每月补贴：<b>{:.2f}</b> 元，公积金缴纳比例：<b>{:.2f}</b>，年终奖为：<b>{:.2f}</b> 元，所在城市：<b>{}</b>".format(base, other_bonus, gjj_ratio, nianzhong, city_cn)
        res += "<br>以下是您每个月的到手收入详情。<br><br>每个月固定扣除社保 {:.2f} 元，扣除公积金 {:.2f} 元".format(baoxian, gongjijin)

        for i in range(12):
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
                res += "<br>【发年终】第 {} 个月税前收入{:.2f} 元（含补贴），扣税 {:.2f} 元，扣除五险一金和个税后总计到手：{:.2f} 元".format(i + 1, all_money, yingna, shuihou)
            else:
                res += "<br>第 {} 个月税前收入{:.2f} 元（含补贴），扣税 {:.2f} 元，扣除五险一金和个税后总计到手：{:.2f} 元".format(i + 1, all_money, yingna, shuihou)
        res += "<br><br>税后总收入：{:.2f} 元，累计公积金为{:.2f} 元".format(sum, gjj)

        return render_template('result.html', result=res)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80, debug=False)