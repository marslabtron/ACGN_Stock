# -*- coding: utf-8 -*
from .. import app
from flask import (
    render_template,
    flash,
    redirect,
    session,
    url_for,
    request,
    jsonify,
)
from app.forms import (
    LoginForm,
    Register,
    Buy_stock
)
from app.handlers import (
    handle,
)


@app.route('/')
@app.route('/index')
def index():
    if 'username' not in session:
        username = None
        user_authority = '0'
    else:
        username = session['username']
        user_authority = handle.get_user_authority(username)
    return render_template('stock_change.html',
                           title='ACGN 交易所',
                           user_authority=user_authority
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = request.form.get('username', None)
        password = request.form.get('password', None)
        remember_me = request.form.get('remember_me', False)
        if handle.authorization(user_name, password):
            session['username'] = user_name
            app.logger.info('loggin')
            return redirect(url_for('index'))
        else:
            flash('login find')
            app.logger.info(
                'loggin faid.user={},pd={},result={}'.format(
                    user_name, password,
                    handle.authorization(user_name, password)))
            return redirect(url_for('login'))
    return render_template('login.html', title="Sign In", form=form)


@app.route('/logout')
def logout():
    # 如果会话中有用户名就删除它。
    # 同时从客户端浏览器中删除 session的 name属性
    flash('logout')
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    # print(form.validate_on_submit())
    if form.validate_on_submit():
        user_name = request.form.get('username', None)
        password = request.form.get('password', None)
        email = request.form.get('email', None)
        if handle.register(user_name, password, email):
            return redirect(url_for('login'))
        else:
            flash('register fail')
            return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)


@app.route('/stock_change/', methods=['GET'])
def stock_change():
    if 'username' not in session:
        username = None
        user_authority = '0'
    else:
        username = session['username']
        user_authority = handle.get_user_authority(username)
    return render_template('stock_change.html',
                           title='Stock Change',
                           user_authority=user_authority
                           )


@app.route('/api/stock_change/', methods=['GET'])
def get_stock_change():
    result = handle.get_stock(limit=request.args.get('limit'),
                              offset=request.args.get('offset'),
                              user_id=request.args.get('id'),
                              name=request.args.get('name'),
                              company=request.args.get('company'),
                              factory=request.args.get('factory'),
                              category=request.args.get('category')
                              )
    return jsonify({
        "msg": "tset",
        "count": result[0],
        "offset": request.args.get('offset'),
        "limit": request.args.get('limit'),
        "company": request.args.get('company'),
        "factory": request.args.get('factory'),
        "name": request.args.get('name'),
        "category": request.args.get('category'),
        "stock": result[1]
    })


@app.route('/stock/', methods=['GET', 'POST'])
def stock():
    if 'username' not in session:
        username = None
        user_authority = '0'
    else:
        username = session['username']
        user_authority = handle.get_user_authority(username)
    form = Buy_stock()
    id = request.args.get('id')
    stock = handle.get_stock(user_id=id)
    stock_order_buy = handle.get_stock_order(stock_id=id, order_type=1)
    if id:
        return render_template(
            'stock.html',
            stocks=stock,
            title="Stock",
            form=form,
            image="{}{}".format(
                "", handle.get_stock_cover(request.args.get('id'))),
            stock_id=request.args.get('id'),
            username=username,
            user_authority=user_authority,
            stock_order_buy=stock_order_buy)
    else:
        return redirect(url_for('index'))


@app.route('/api/stock/', methods=['GET'])
def get_stock_order():
    stock_id = request.args.get('id')
    order_type = request.args.get('type')
    # app.logger.info('id:,type:'.format(stock_id, order_type))
    return jsonify({
        "msg": "tset",
        "body": handle.get_stock_order(
            stock_id=stock_id,
            order_type=order_type)
    })


@app.route('/api/order_submit/', methods=['POST'])
def order_submit():
    msg = handle.buy_stock(
        stock_id=request.get_json().get('stock_id'),
        order_number=request.get_json().get('order_number'),
        order_price=request.get_json().get('order_price'),
        user_name=session['username'],
        order_type=request.get_json().get('order_type')
    )
    app.logger.info(
        "stock_id:{},order_number:{},order_price:{},order_type:{}".format(
            request.get_json().get('stock_id'),
            request.get_json().get('order_number'),
            request.get_json().get('order_price'),
            request.get_json().get('order_type'),
        ))
    return jsonify({
        'msg': msg,
        'body': request.get_json()
    })


@app.route('/user/', methods=['GET', 'POST'])
def user():
    id = request.args.get('id')
    user, user_stock = handle.get_user_stock(id)
    if user:
        return render_template('user.html',
                               username=user.nickname,
                               user=user,
                               user_stock=user_stock)
    else:
        return redirect(url_for('index'))


@app.route('/stock_apply/', methods=['GET'])
def stock_apply():
    if 'username' in session:
        username = session['username']
    else:
        username = None
    return render_template('stock_apply.html', username=username)


@app.route('/api/stock_apply/', methods=['POST'])
def stock_apply_submit():
    # print(request.get_json())
    try:
        msg = handle.stock_apply(user_id=request.get_json().get('user_id'),
                                 stock_name=request.get_json().get('stock_name'),
                                 stock_image=request.get_json().get('stock_image'),
                                 stock_cover=request.get_json().get('stock_cover'),
                                 stock_introduction=request.get_json().get('stock_introduction'),
                                 apply_status=0)
    except ValueError:
        msg = '输入参数异常'

    return jsonify({
        "msg": msg
    })


@app.route('/api/user_id/', methods=['GET'])
def get_userid():
    if 'username' in session:
        username = session['username']
        userid = handle.get_userid(username)
        msg = 'ok'
        return jsonify({
            "msg": msg,
            "userid": userid
        })

    else:
        username = 'None'
        msg = '没有用户'
        return jsonify({
            "msg": msg,
            "userid": username
        })


@app.route('/api/user_id_authority/', methods=['GET'])
def get_userid_authority():
    if 'username' in session:
        username = session['username']
        user_authority = handle.get_user_authority(username)
        msg = 'ok'
        return jsonify({
            "msg": msg,
            "user_id_authority": user_authority
        })

    else:
        user_authority = 'None'
        msg = '没有用户'
        return jsonify({
            "msg": msg,
            "user_authority": user_authority
        })


@app.route('/apply_review/', methods=['GET'])
def apply_review():
    if 'username' in session:
        username = session['username']
        user_authority = handle.get_user_authority(username)
    else:
        username = None
    return render_template('apply_review.html',
                           username=username,
                           user_authority=user_authority)


@app.route('/api/get_apply/', methods=['GET'])
def get_apply():
    stock_apply = handle.get_apply()
    return jsonify({
        "json": stock_apply
    })


@app.route('/api/apple_pass/', methods=['POST'])
def apple_pass():
    if 'username' in session:
        username = session['username']
        user_authority = handle.get_user_authority(username)
        if user_authority == "1":
            msg = handle.review_pass(request.get_json().get('id'))
            return jsonify({
                "msg": msg
            })
        else:
            return jsonify({
                "msg": "用户权限不够"
            })
    else:
        return jsonify({
            "msg": "用户不存在"
        })


@app.route('/api/Magnet/', methods=['POST'])
def add_Magnet():
    if 'username' in session:
        msg = handle.addMagnet(
            stock_id=request.get_json().get('stock_id'),
            Magnet=request.get_json().get('Magnet'),
            user_id=handle.get_userid(session['username']))
        return jsonify({
            "msg": msg
        })
    else:
        return jsonify({
            "msg": "必须登录才可以提交"
        })
    pass


@app.route('/api/Magnet/', methods=['GET'])
def get_Magnet():
    # print(request.args.get('stock_id'))
    magnet = handle.getMagenet(stock_id=request.args.get('stock_id'))
    return jsonify({
        "msg": 'ok',
        "Magnet": magnet
    })
    pass


@app.route('/api/stockinfo/', methods=['GET'])
def get_Stock_info():
    json = handle.get_stock_info(stock_id=request.args.get('stock_id'))
    return jsonify({
        "msg": "ok",
        "json": json
    })
    pass
