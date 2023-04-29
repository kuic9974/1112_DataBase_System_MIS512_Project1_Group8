from http.client import REQUESTED_RANGE_NOT_SATISFIABLE
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp
import random
import os
import string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/beverage'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')


def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER']
    return config


@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.beverageManager'))


@manager.route('/beverageManager', methods=['GET', 'POST'])
@login_required
def beverageManager():
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))

    if 'delete' in request.values:
        bid = request.values.get('delete')
        ordercount = OrderList.get_order_count_by_bid(bid)

        if (ordercount > 0):
            flash('failed')
        else:
            data = Beverage.get_beverage(bid)
            Beverage.delete_beverage(bid)

    elif 'edit' in request.values:
        bid = request.values.get('edit')
        return redirect(url_for('manager.edit', bid=bid))

    beverage_data = beverage()
    return render_template('beverageManager.html', beverage_data=beverage_data, user=current_user.name)


@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while (data != None):
            number = str(random.randrange(10000, 99999))
            en = random.choice(string.ascii_letters)
            bid = en + number
            data = Beverage.get_beverage(bid)

        name = request.values.get('name')
        price = request.values.get('price')

        if (len(name) < 1 or len(price) < 1):
            return redirect(url_for('manager.beverageManager'))

        ordercount = Beverage.check_beverage_name_exists(name)

        if (ordercount > 0):
            flash('AddBeverageFailed')
            return redirect(url_for('manager.beverageManager'))

        Beverage.add_beverage(
            {
                'bid': bid,
                'name': name,
                'price': price
            }
        )

        return redirect(url_for('manager.beverageManager'))

    return render_template('beverageManager.html')


@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Beverage.update_beverage(
            {
                'bname': request.values.get('bname'),
                'bid': request.values.get('bid'),
                'price': request.values.get('price')
            }
        )
        return redirect(url_for('manager.beverageManager'))

    else:
        beverage = show_info()
        return render_template('edit.html', data=beverage, user=current_user.name)


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        # orderdetail_row = OrderList_Detail.get_all_order_detail_history()
        # orderdetailHistory = []

        # for j in orderdetail_row:
        #     orderdetailhistory_did = j[0]
        #     orderdetailhistory_oid = j[1]
        #     orderdetailhistory_bname = j[2]
        #     orderdetailhistory_price = j[3]
        #     orderdetailhistory_sugar = j[4]
        #     orderdetailhistory_ice = j[5]
        #     orderdetailhistory_mid = j[6]

        #     orderdetailhistory_choicelist = Choice.get_choice_content(
        #         {
        #             'did': orderdetailhistory_did,
        #             'oid': orderdetailhistory_oid,
        #             'mid': orderdetailhistory_mid
        #         }
        #     )

        #     orderdetailhistory_choicelist = [choice[0].strip(
        #         "()") for choice in orderdetailhistory_choicelist]
        #     orderdetailhistory_choice = ",".join(orderdetailhistory_choicelist)

        #     if len(orderdetailhistory_choicelist) > 0:
        #         orderdetailhistory_subtotal = orderdetailhistory_price + \
        #             len(orderdetailhistory_choicelist) * 10
        #     else:
        #         orderdetailhistory_subtotal = orderdetailhistory_price

        #     temp = {
        #         '訂單編號': orderdetailhistory_oid,
        #         '飲品名稱': orderdetailhistory_bname,
        #         '飲品單價': orderdetailhistory_price,
        #         '甜度': orderdetailhistory_sugar,
        #         '冰塊': orderdetailhistory_ice,
        #         '加料': orderdetailhistory_choice,
        #         '小計': orderdetailhistory_subtotal
        #     }

        #     orderdetailHistory.append(temp)

        # data = OrderList.get_all_order()

        # orderHistory = []

        # for i in data:
        #     orderhistory_oid = i[0]
        #     totalprice = 0
        #     for x in orderdetailHistory:
        #         if (x['訂單編號'] == orderhistory_oid):
        #             totalprice += x['小計']

        #     order_datetime = i[7]
        #     order_mid = i[1]
        #     order_name = i[2]
        #     order_member_name = i[8]
        #     temp = {
        #         '訂單編號': orderhistory_oid,
        #         '訂單會員編號': order_mid,
        #         '訂單會員姓名': order_member_name,
        #         '訂購人姓名': order_name,
        #         '訂單總價': totalprice,
        #         '訂單時間': order_datetime
        #     }
        #     orderHistory.append(temp)

        data = OrderList.get_all_order_with_totalprice()

        orderHistory = []

        for i in data:

            order_mid = i[0]
            order_member_name = i[1]
            order_name = i[2]
            orderhistory_oid = i[3]
            totalprice = i[4]
            order_datetime = i[5]

            temp = {
                '訂單編號': orderhistory_oid,
                '訂單會員編號': order_mid,
                '訂單會員姓名': order_member_name,
                '訂購人姓名': order_name,
                '訂單總價': totalprice,
                '訂單時間': order_datetime
            }
            orderHistory.append(temp)

        orderdetail_row = OrderList_Detail.get_all_order_detail_with_price()
        orderdetailHistory = []

        for j in orderdetail_row:
            orderdetailhistory_did = j[0]
            orderdetailhistory_oid = j[1]
            orderdetailhistory_sugar = j[4]
            orderdetailhistory_ice = j[5]
            orderdetailhistory_dRemark = j[6]
            orderdetailhistory_bname = j[7]
            orderdetailhistory_price = j[8]
            orderdetailhistory_choice = j[9]
            orderdetailhistory_subtotal = j[10]

            temp = {
                '訂單編號': orderdetailhistory_oid,
                '明細編號': orderdetailhistory_did,
                '飲品名稱': orderdetailhistory_bname,
                '飲品單價': orderdetailhistory_price,
                '甜度': orderdetailhistory_sugar,
                '冰塊': orderdetailhistory_ice,
                '加料': orderdetailhistory_choice,
                '單品備註': orderdetailhistory_dRemark,
                '小計': orderdetailhistory_subtotal
            }

            orderdetailHistory.append(temp)
    return render_template('orderManager.html', data=orderHistory, detail=orderdetailHistory, user=current_user.name)


def beverage():
    beverage_row = Beverage.get_all_beverage()
    beverage_data = []
    for i in beverage_row:
        beverage = {
            '飲品編號': i[0],
            '飲品名稱': i[1],
            '飲品單價': i[2]
        }
        beverage_data.append(beverage)
    return beverage_data


def show_info():
    bid = request.args['bid']
    data = Beverage.get_beverage(bid)
    bname = data[1]
    price = data[2]

    beverage = {
        '飲品編號': bid,
        '飲品名稱': bname,
        '飲品單價': price
    }
    return beverage
