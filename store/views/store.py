import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random
import string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import *
import json  # 引用json模組

beveragestore = Blueprint('store', __name__, template_folder='../templates')

orderlist_detail = []
beverage = []


@beveragestore.route('/', methods=['GET', 'POST'])
@login_required
def store():
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    beverage_data = Beverage.get_all_beverage()
    beverages = []
    for i in beverage_data:
        temp = {
            'bname': i[1],
            'price': i[2]
        }
        beverages.append(temp)
    return render_template('store.html', beverages=beverages, user=current_user.name)


@beveragestore.route('/order', methods=['GET', 'POST'])
@login_required  # 使用者登入後才可以看
def order():

    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if request.method == 'POST':
        if "addDetail" in request.values:

            number = str(random.randrange(100000, 999999))
            en = random.choice(string.ascii_letters)
            did = en + number

            selected_beverage = request.form.get('bname')
            selected_beverage_dict = string_to_dict(selected_beverage)
            bid = selected_beverage_dict['bid']
            bname = selected_beverage_dict['bname']
            sugar = request.form.get('sugar')
            ice = request.form.get('ice')
            price = selected_beverage_dict['price']
            choiceStr = request.form.getlist('choice')
            choice = ",".join(choiceStr)
            choicelist = choice.split(',')
            
            if sugar == None:
                flash('Sugar is null')
                return redirect(url_for('store.order'))

            if ice == None:
                flash('Ice is null')
                return redirect(url_for('store.order'))

            if choice == "":
                subtotal = price
            else:
                subtotal = price + len(choicelist) * 10

            dRemark = request.form.get('dRemark')
            orderlist_detail.append(
                {'did': did, 'bid': bid, 'bname': bname, 'sugar': sugar, 'ice': ice, 'price': price, 'choice': choice, 'subtotal': subtotal, 'dRemark': dRemark})

            return redirect(url_for('store.order'))
        if "delete" in request.values:
            target_did = request.values.get("delete")
            # index = None
            # for i, d in enumerate(orderlist_detail):
            #     if d['did'] == target_did:
            #         index = i
            #         break
            # del orderlist_detail[index]
            del_list(orderlist_detail, 'did', target_did)
            return redirect(url_for('store.order'))
        if "next_step" in request.values:
            if len(orderlist_detail) == 0:
                flash('No Orderlist Detail')
                return redirect(url_for('store.order'))

            return redirect(url_for('store.orderInfo'))
    else:
        totalprice = 0
        for detail in orderlist_detail:
            totalprice += detail['subtotal']

        beverage = get_all_beverage()
        return render_template('order.html', data=orderlist_detail, beverage=beverage, totalprice=totalprice, user=current_user.name)


@beveragestore.route('/orderInfo', methods=['GET', 'POST'])
@login_required  # 使用者登入後才可以看
def orderInfo():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if request.method == 'POST':
        if "previous_step" in request.values:
            # totalprice = 0
            # for detail in orderlist_detail:
            #     totalprice += detail['subtotal']
            # beverage = get_all_beverage()
            # return render_template('order.html', data=orderlist_detail, beverage=beverage, totalprice=totalprice, user=current_user.name)
            return redirect(url_for('store.order'))
        if "sendorder" in request.values:
            number = str(random.randrange(100000, 999999))
            en = random.choice(string.ascii_letters)
            oid = en + number
            mid = current_user.id
            oName = request.form.get('oName')
            phone = request.form.get('phone')
            address = request.form.get('address')
            payment = request.form.get('payment')
            oRemark = request.form.get('oRemark')

            OrderList.add_order(
                {
                    'oid': oid,
                    'mid': mid,
                    'oName': oName,
                    'phone': phone,
                    'address': address,
                    'payment': payment,
                    'oRemark': oRemark
                }
            )

            for datarow in orderlist_detail:
                # detail_dict = string_to_dict(datarow)

                did = datarow['did']
                bid = datarow['bid']
                # sugar = detail_dict['sugar']
                # ice = detail_dict['ice']
                # dRemark = detail_dict['dRemark']
                sugar = datarow['sugar']
                ice = datarow['ice']
                dRemark = datarow['dRemark']

                OrderList_Detail.add_order_detail(
                    {
                        'did': did,
                        'oid': oid,
                        'mid': mid,
                        'bid': bid,
                        'sugar': sugar,
                        'ice': ice,
                        'dRemark': dRemark
                    }
                )
                choice_str = ""
                # choice_str = detail_dict['choice']
                choice_str = datarow['choice']
                if choice_str != "":
                    choicelist = choice_str.split(',')
                    for content in choicelist:
                        Choice.add_choice(
                            {
                                'did': did,
                                'oid': oid,
                                'mid': mid,
                                'bid': bid,
                                'content': content,
                                'amount': 1
                            }
                        )
            orderlist_detail.clear()  # 送出訂單後清空order.html的頁面資料
            return render_template('complete.html', user=current_user.name)
    else:
        return render_template('orderInfo.html', data=orderlist_detail, user=current_user.name)


@beveragestore.route('/orderHistory')
@login_required  # 使用者登入後才可以看
def orderHistory():
    if "oid" in request.args:
        pass

    user_id = current_user.id

    # orderdetail_row = OrderList_Detail.get_order_detail_history(user_id)
    # orderdetailHistory = []

    # for j in orderdetail_row:
    #     orderdetailhistory_did = j[0]
    #     orderdetailhistory_oid = j[1]
    #     orderdetailhistory_bname = j[2]
    #     orderdetailhistory_price = j[3]
    #     orderdetailhistory_sugar = j[4]
    #     orderdetailhistory_ice = j[5]

    #     orderdetailhistory_choicelist = Choice.get_choice_content(
    #         {
    #             'did': orderdetailhistory_did,
    #             'oid': orderdetailhistory_oid,
    #             'mid': user_id
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

    # data = OrderList.get_order(user_id)

    # orderHistory = []

    # for i in data:
    #     orderhistory_oid = i[0]
    #     totalprice = 0
    #     for x in orderdetailHistory:
    #         if (x['訂單編號'] == orderhistory_oid):
    #             totalprice += x['小計']

    #     order_datetime = i[7]
    #     temp = {
    #         '訂單編號': orderhistory_oid,
    #         '訂單總價': totalprice,
    #         '訂單時間': order_datetime
    #     }
    #     orderHistory.append(temp)

    data = OrderList.get_all_order_with_totalprice_by_userid(user_id)

    orderHistory = []

    for i in data:
        orderhistory_oid = i[3]
        totalprice = i[4]
        order_datetime = i[5]

        temp = {
            '訂單編號': orderhistory_oid,
            '訂單總價': totalprice,
            '訂單時間': order_datetime
        }
        orderHistory.append(temp)

    orderdetail_row = OrderList_Detail.get_all_order_detail_with_price_by_userid(user_id)
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

    return render_template('orderHistory.html', data=orderHistory, detail=orderdetailHistory, user=current_user.name)


def del_list(list, key, target_value):
    index = None
    for i, d in enumerate(list):
        if d[key] == target_value:
            index = i
            break
    del list[index]


def string_to_dict(str):
    str = str.replace("'", "\"")
    dict = json.loads(str)
    return dict


def get_all_beverage():
    beverage_row = Beverage.get_all_beverage()
    beverage_data = []
    for i in beverage_row:
        beverage = {
            'bid': i[0],
            'bname': i[1],
            'price': i[2]
        }
        beverage_data.append(beverage)
    return beverage_data
