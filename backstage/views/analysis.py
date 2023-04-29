from flask import render_template, Blueprint
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import Analysis, Beverage

analysis = Blueprint('analysis', __name__, template_folder='../templates')


@analysis.route('/dashboard')
@login_required
def dashboard():
    revenue_month = []
    revenue_day = []
    ordercount_month = []
    for i in range(1, 13):
        row = Analysis.month_price(i)

        if not row:
            revenue_month.append(0)
        else:
            for j in row:
                revenue_month.append(j[1])

        row = Analysis.month_count(i)

        if not row:
            ordercount_month.append(0)
        else:
            for k in row:
                ordercount_month.append(k[1])

    row = Analysis.member_sale()

    totalpriceList = []
    nameList = []
    counter = 0

    for i in row:
        counter = counter + 1
        totalpriceList.append(i[0])
    for j in row:
        nameList.append(j[2])

    counter = counter - 1

    row = Analysis.member_sale_count()
    countList = []

    for i in row:
        countList.append(i[0])

    row = Analysis.beverage_sale_count()
    beverage_sale_count = []
    for i in row:
        temp = {
            'value': i[2],
            'name': i[1]
        }
        beverage_sale_count.append(temp)

    data = Beverage.get_all_name()
    beverage_nameList = [choice[0].strip(
        "()") for choice in data]

    return render_template('dashboard.html', counter=counter, revenue_month=revenue_month, ordercount_month=ordercount_month, totalpriceList=totalpriceList, nameList=nameList, countList=countList, beverage_sale_count=beverage_sale_count, beverage_nameList=beverage_nameList, user=current_user.name)
