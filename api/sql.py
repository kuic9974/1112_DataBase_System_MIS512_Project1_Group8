from typing import Optional
from link import *


class DB():
    def connect():
        cursor = connection.cursor()
        return cursor

    def prepare(sql):
        cursor = DB.connect()
        cursor.prepare(sql)
        return cursor

    def execute(cursor, sql):
        cursor.execute(sql)
        return cursor

    def execute_input(cursor, input):
        cursor.execute(None, input)
        return cursor

    def fetchall(cursor):
        return cursor.fetchall()

    def fetchone(cursor):
        return cursor.fetchone()

    def commit():
        connection.commit()


class Member():
    def get_member(account):
        sql = "SELECT ACCOUNT, PASSWORD, MID, IDENTITY, NAME FROM MEMBER WHERE ACCOUNT = :account"
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'account': account}))

    def get_all_account():
        sql = "SELECT ACCOUNT FROM MEMBER"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def create_member(input):
        sql = 'INSERT INTO MEMBER VALUES (null, :name, :account, :password, :identity)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def get_role(userid):
        sql = 'SELECT IDENTITY, NAME FROM MEMBER WHERE MID = :mid '
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'mid': userid}))


class Beverage():
    def count():
        sql = 'SELECT COUNT(*) FROM beverage'
        return DB.fetchone(DB.execute(DB.connect(), sql))

    def check_beverage_name_exists(bname):
        sql = 'SELECT count(*) FROM beverage WHERE bname = :bname'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'bname': bname}))[0]

    def get_beverage(bid):
        sql = 'SELECT * FROM beverage WHERE bid = :bid'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'bid': bid}))

    def get_all_beverage():
        sql = "SELECT * FROM beverage"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_all_name():
        sql = "SELECT bNAME FROM beverage"
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_name(bid):
        sql = 'SELECT bNAME FROM beverage WHERE bid = :bid'
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'bid': bid}))[0]

    def add_beverage(input):
        sql = 'INSERT INTO beverage VALUES (:bid, :name , :price)'

        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def delete_beverage(bid):
        sql = 'DELETE FROM beverage WHERE bid = :bid '
        DB.execute_input(DB.prepare(sql), {'bid': bid})
        DB.commit()

    def update_beverage(input):
        sql = 'UPDATE beverage SET bname=:bname , price=:price WHERE bid=:bid'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()


class OrderList():
    def add_order(input):
        sql = 'INSERT INTO OrderList VALUES (:oid, :mid, :oName, :phone, :address, :payment, :oRemark, sysdate)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def get_order(userid):
        sql = 'SELECT * FROM OrderList WHERE MID = :mid ORDER BY datetime DESC'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'mid': userid}))

    def get_all_order():
        sql = 'SELECT a.*,b.name FROM OrderList a join Member b on a.mid = b.mid ORDER BY a.datetime DESC'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_order_count_by_bid(bid):
        sql = 'Select count(*) from ORDERLIST a join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid where b.bid= :bid'
        # [0]是將 tuple 中的元素取出，不然(result,)會造成程式錯誤
        return DB.fetchone(DB.execute_input(DB.prepare(sql), {'bid': bid}))[0]

    def get_all_order_with_totalprice():
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, ccc.oname, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT * From Order_TotalPrice '
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_all_order_with_totalprice_by_userid(userid):
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, ccc.oname, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT * From Order_TotalPrice '
        sql += 'Where 1=1 '
        sql += 'and mid = :mid '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'mid': userid}))

class OrderList_Detail():
    def add_order_detail(input):
        sql = 'INSERT INTO OrderList_Detail VALUES (:did, :oid, :mid, :bid, :sugar, :ice, :dRemark)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def get_order_detail_history(userid):
        sql = 'SELECT a.did, a.oid, b.bname , b.price, a.sugar, a.ice FROM OrderList_Detail a Join BEVERAGE b on a.bid = b.bid WHERE MID = :mid'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'mid': userid}))

    def get_all_order_detail_history():
        sql = 'SELECT a.did, a.oid, b.bname , b.price, a.sugar, a.ice, a.mid FROM OrderList_Detail a Join BEVERAGE b on a.bid = b.bid'
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_all_order_detail_with_price():
        sql = 'WITH Choice_Count as ('
        sql += "    select mid,oid,did,bid, listagg(content, ',') within group(ORDER BY did,oid,mid,bid) AS content, count(*) as Choice_Count "
        sql += '    from CHOICE '
        sql += '    group by mid,oid,did,bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,did,bid,content,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid,did,bid,content '
        sql += '), OrderDetail_SubTotalPrice as ( '
        sql += '    select a.*, c.bname , c.price, b.content , c.price + nvl(Choice_Sum_Price,0) as Subtotal '
        sql += '    from ORDERLIST_DETAIL a '
        sql += '    left join Choice_Price b on a.did = b.did and a.oid = b.oid and a.mid = b.mid and a.bid = b.bid '
        sql += '    join BEVERAGE c on a.bid = c.bid '
        sql += ') '
        sql += 'Select * from OrderDetail_SubTotalPrice '
        return DB.fetchall(DB.execute(DB.connect(), sql))

    def get_all_order_detail_with_price_by_userid(userid):
        sql = 'WITH Choice_Count as ('
        sql += "    select mid,oid,did,bid, listagg(content, ',') within group(ORDER BY did,oid,mid,bid) AS content, count(*) as Choice_Count "
        sql += '    from CHOICE '
        sql += '    group by mid,oid,did,bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,did,bid,content,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid,did,bid,content '
        sql += '), OrderDetail_SubTotalPrice as ( '
        sql += '    select a.*, c.bname , c.price, b.content , c.price + nvl(Choice_Sum_Price,0) as Subtotal '
        sql += '    from ORDERLIST_DETAIL a '
        sql += '    left join Choice_Price b on a.did = b.did and a.oid = b.oid and a.mid = b.mid and a.bid = b.bid '
        sql += '    join BEVERAGE c on a.bid = c.bid '
        sql += ') '
        sql += 'Select * from OrderDetail_SubTotalPrice '
        sql += 'Where 1=1 '
        sql += 'and mid = :mid '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'mid': userid}))

class Choice():
    def add_choice(input):
        sql = 'INSERT INTO Choice VALUES (:did, :oid, :mid, :bid, :content, :amount)'
        DB.execute_input(DB.prepare(sql), input)
        DB.commit()

    def get_choice_content(input):
        sql = 'SELECT content FROM Choice WHERE mid = :mid and did = :did and oid = :oid'
        return DB.fetchall(DB.execute_input(DB.prepare(sql), input))


class Analysis():
    def month_price(i):
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    Where 1=1 '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    where 1=1 '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT EXTRACT(MONTH FROM ORDERTIME), SUM(totalprice) FROM Order_TotalPrice WHERE EXTRACT(MONTH FROM ORDERTIME)=:mon GROUP BY EXTRACT(MONTH FROM ORDERTIME) '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {"mon": i}))

    def month_count(i):
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    Where 1=1 '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    where 1=1 '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT EXTRACT(MONTH FROM ORDERTIME), COUNT(OID) FROM Order_TotalPrice WHERE EXTRACT(MONTH FROM ORDERTIME)=:mon GROUP BY EXTRACT(MONTH FROM ORDERTIME) '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {"mon": i}))

    def member_sale():
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    Where 1=1 '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    where 1=1 '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT SUM(totalprice), b.MID, b.NAME '
        sql += 'FROM Order_TotalPrice a '
        sql += 'JOIN MEMBER b on a.MID = b.MID '
        sql += 'WHERE 1=1 '
        sql += 'AND b.IDENTITY = :identity GROUP BY b.MID, b.NAME ORDER BY SUM(totalprice) DESC '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'identity': 'user'}))

    def member_sale_count():
        sql = 'WITH Order_Price AS '
        sql += '( '
        sql += '    Select a.oid,a.mid,d.name as member_name,sum(c.price) as Beverage_Sum_Price from ORDERLIST a '
        sql += '    join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += '    join BEVERAGE c on b.bid = c.bid '
        sql += '    join MEMBER d on a.mid = d.mid '
        sql += '    Where 1=1 '
        sql += '    group by a.oid,a.mid,d.name '
        sql += '), Choice_Count as ( '
        sql += '    select cc.mid,cc.oid,cc.did,cc.bid,count(*) as Choice_Count '
        sql += '    from Order_Price aa '
        sql += '    join ORDERLIST_DETAIL bb on aa.oid = bb.oid and aa.mid = bb.mid '
        sql += '    join CHOICE cc on bb.did = cc.did and bb.oid = cc.oid and bb.mid = cc.mid and bb.bid = cc.bid '
        sql += '    where 1=1 '
        sql += '    group by cc.mid,cc.oid,cc.did,cc.bid '
        sql += '), Choice_Price as ( '
        sql += '    select mid,oid,sum(Choice_Count)*10 as Choice_Sum_Price '
        sql += '    from Choice_Count '
        sql += '    group by mid,oid '
        sql += '), Order_TotalPrice as ( '
        sql += '    select aaa.mid, aaa.member_name, aaa.oid, Beverage_Sum_Price + nvl(Choice_Sum_Price,0) as totalprice , ccc.datetime as ORDERTIME '
        sql += '    from Order_Price aaa '
        sql += '    left join Choice_Price bbb on aaa.mid = bbb.mid and aaa.oid = bbb.oid '
        sql += '    join ORDERLIST ccc on  aaa.mid = ccc.mid and aaa.oid = ccc.oid '
        sql += '    order by ccc.datetime desc '
        sql += ') '
        sql += 'SELECT COUNT(*), b.MID, b.NAME '
        sql += 'FROM Order_TotalPrice a '
        sql += 'JOIN MEMBER b on a.MID = b.MID '
        sql += 'WHERE 1=1 '
        sql += 'AND b.IDENTITY = :identity GROUP BY b.MID, b.NAME ORDER BY COUNT(*) DESC '
        return DB.fetchall(DB.execute_input(DB.prepare(sql), {'identity': 'user'}))

    def beverage_sale_count():
        sql = 'Select c.bid, c.bname, count(*) '
        sql += 'from ORDERLIST a '
        sql += 'join ORDERLIST_DETAIL b on a.oid = b.oid and a.mid = b.mid '
        sql += 'join BEVERAGE c on b.bid = c.bid '
        sql += 'group by c.bid, c.bname '
        sql += 'ORDER BY count(*) DESC '
        return DB.fetchall(DB.execute(DB.connect(), sql))