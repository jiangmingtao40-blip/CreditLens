import pymysql

# 数据库连接配置
config = {
    'host': 'localhost',
    'user': 'single_open',
    'password': '111111',
    'database': 'single_open',
    'port': 3306,
    'charset': 'utf8mb4'
}

try:
    # 连接数据库
    conn = pymysql.connect(**config)
    cursor = conn.cursor()
    
    # 创建邀请记录表
    create_invite_table = """
    CREATE TABLE IF NOT EXISTS credit_invite (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
        inviter_id BIGINT NOT NULL COMMENT '邀请人ID',
        invited_id BIGINT NOT NULL COMMENT '被邀请人ID',
        commission DECIMAL(10,2) DEFAULT 0 COMMENT '获得佣金',
        status TINYINT DEFAULT 0 COMMENT '状态：0-待结算 1-已结算',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-否 1-是',
        INDEX idx_inviter_id (inviter_id),
        INDEX idx_invited_id (invited_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='邀请记录表';
    """
    cursor.execute(create_invite_table)
    print("创建 credit_invite 表成功")
    
    # 创建提现记录表
    create_withdraw_table = """
    CREATE TABLE IF NOT EXISTS credit_withdraw (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
        user_id BIGINT NOT NULL COMMENT '用户ID',
        amount DECIMAL(10,2) NOT NULL COMMENT '提现金额',
        status TINYINT DEFAULT 0 COMMENT '状态：0-审核中 1-已通过 2-已拒绝 3-已打款',
        account_type VARCHAR(20) COMMENT '提现账户类型',
        account_no VARCHAR(100) COMMENT '提现账户号',
        account_name VARCHAR(100) COMMENT '账户姓名',
        remark VARCHAR(500) COMMENT '备注',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-否 1-是',
        INDEX idx_user_id (user_id),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提现记录表';
    """
    cursor.execute(create_withdraw_table)
    print("创建 credit_withdraw 表成功")
    
    # 创建信用订单表
    create_order_table = """
    CREATE TABLE IF NOT EXISTS credit_order (
        id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
        order_no VARCHAR(32) NOT NULL UNIQUE COMMENT '订单号',
        user_id BIGINT NOT NULL COMMENT '用户ID',
        type VARCHAR(20) COMMENT '订单类型',
        amount DECIMAL(10,2) NOT NULL COMMENT '金额',
        status VARCHAR(20) DEFAULT 'pending' COMMENT '状态：pending-待支付 success-支付成功 canceled-已取消',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        is_deleted TINYINT DEFAULT 0 COMMENT '是否删除：0-否 1-是',
        INDEX idx_user_id (user_id),
        INDEX idx_order_no (order_no),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='信用订单表';
    """
    cursor.execute(create_order_table)
    print("创建 credit_order 表成功")
    
    conn.commit()
    print("所有表创建成功！")
    
except Exception as e:
    print(f"创建表时发生错误: {e}")
    conn.rollback()
finally:
    if conn:
        conn.close()
