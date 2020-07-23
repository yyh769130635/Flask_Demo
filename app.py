from flask import Flask, send_from_directory
from flask import render_template
from flask import request
import time
import json
import db
from pyecharts.charts import Bar
from pyecharts.charts import Pie
from pyecharts.charts import Line
from pyecharts import options as opts
from jinja2 import Markup
import os
import datetime
import xlwt
app = Flask(__name__)

@app.route('/')
def hello_world():
    return hello_world2()

@app.route('/hello')
def hello_world2():
    data= "hello data"
    return render_template("hello.html",data=data)

#url路径的方式
@app.route("/user/<username>",methods=["GET","POST"])
def get_user(username):
    return "hello %s " %username

#url查询参数
@app.route("/data",methods=["POST","GET"])
def test_data():
    ## 接受url后面的参数
    # print(request.args)
    # print(request.args.get('a'),request.args.get('a'))
    # print(request.headers)

    ## json
    # print(request.data)
    # import json
    # print(json.loads(request.data))

    ## cookies
    # print(request.cookies)
    # print(request.cookies.get("token"))

    ## form
    print(request.form)
    print(request.form.get("username"),request.form.get("password"))

    return "success"

@app.route("/user_template")
def user_template():
    datas=[(1,"name1"),(2,"name2"),(3,"name3")]
    title="学生信息"
    return render_template("user_template.html",datas=datas,title=title)


def read_pvuv_data():
    '''
    read pv uv data
    :return: list,ele:(pdate,pv uv)
    '''
    data = []
    with open("./data/pvuv.csv", 'r', encoding='UTF-8') as fin:
        is_first_line = True
        for line in fin:
            if is_first_line:
                is_first_line = False
                continue
            line = line[:-1]
            # print(line.split(","))
            pdate, pv, uv = line.split(",")
            data.append((pdate, pv, uv))
    return data


@app.route("/pvuv")
def pvuv():
    #read file
    data=read_pvuv_data()
    # return html
    return render_template("pvuv.html",data=data)

@app.route("/getjson")
def getjson():
    #read file
    data=read_pvuv_data()
    # return html
    return json.dumps(data)

@app.route('/show_add_user')
def show_add_user():
    return render_template("show_add_user.html")


@app.route('/do_add_user',methods=["POST"])
def do_add_user():
    print(request.form)
    name = request.form.get("name")
    sex = request.form.get("sex")
    age = request.form.get("age")
    email = request.form.get("email")
    sql=f"""
        insert into user (name,sex,age,email)
        values('{name}','{sex}','{age}','{email}')
    """
    print(sql)
    db.insert_or_update_date(sql)
    return "success"

@app.route('/show_users')
def show_users():
    sql = "select id, name from user"
    datas=db.query_data(sql)
    return render_template("show_users.html",datas=datas)


@app.route('/show_user/<user_id>')
def show_user(user_id):
    sql= "select * from user where id="+user_id
    datas=db.query_data(sql)
    user=datas[0]
    return render_template("show_user.html",user=user)


@app.route('/show_echarts')
def show_echarts():
    xdatas = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    ydatas = [820, 932, 901, 934, 1290, 1330, 1320]
    return render_template("show_echarts.html",
                           xdatas = Markup(json.dumps(xdatas)),#转成字符串的形式
                           ydatas = json.dumps(ydatas))


@app.route('/show_pyecharts')
def show_pyecharts():
    bar = (
        Bar()
            .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
            .add_yaxis("商家A", [5, 20, 36, 10, 75, 90])
    )
    return render_template("show_pyecharts.html",
                           bar_options=bar.dump_options())


def get_pie() -> Pie:
    sql="""
        select sex,count(1) as cnt from user group by sex
    """
    datas=db.query_data(sql)
    c = (
        Pie()
            .add("",[(data["sex"],data["cnt"]) for data in datas])
            .set_global_opts(title_opts=opts.TitleOpts(title="Pie-基本示例"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    return c


def get_bar() -> Bar:
    sql = """
            select sex,count(1) as cnt from user group by sex
        """
    datas = db.query_data(sql)
    c = (
        Bar()
            .add_xaxis([data["sex"] for data in datas])
            .add_yaxis("数量", [data["cnt"] for data in datas])
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例"))
    )
    return c

def get_line() -> Line:
    sql = """
            select pdate,pv,uv from pvuv
        """
    datas = db.query_data(sql)
    c = (
        Line()
            .add_xaxis([data["pdate"] for data in datas])
            .add_yaxis("pv",[data["pv"] for data in datas])
            .add_yaxis("uv",[data["uv"] for data in datas])
            .set_global_opts(title_opts=opts.TitleOpts(title="Line-基本示例"))
    )
    return c

@app.route('/show_myecharts')
def show_myecharts():
    pie = get_pie()
    bar = get_bar()
    line = get_line()
    return render_template("show_mycharts.html",
                           pie_options=pie.dump_options(),
                           bar_options=bar.dump_options(),
                          line_options=line.dump_options())

def generate_excel(data_dir,fname):
    fpath = os.path.join(data_dir,fname)
    workbook = xlwt.Workbook(encoding="utf-8")
    worksheet = workbook.add_sheet("pvuv")
    for idx, name in enumerate(["日期","pv","uv"]):
        worksheet.write(0,idx,name)
    datas=db.query_data("select * from pvuv")
    for row,data in enumerate(datas):
        for col,kv in enumerate(data.items()):
            worksheet.write(row+1,col,kv[1])
    workbook.save(fpath)


@app.route("/download_pvuv_excel")
def downloads_pvuv():
    data_dir = os.path.join(app.root_path,"downloads")
    now_time = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))
    print(now_time)
    # now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fname = f"pvuv_{now_time}.xls"
    generate_excel(data_dir,fname)

    return send_from_directory(data_dir, fname,as_attachment=True)


if __name__ == '__main__':
    app.run()
