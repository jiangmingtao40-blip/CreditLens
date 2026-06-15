-- =============================================
-- 征信报告AI解析系统 - 表结构创建
-- 使用 single_open 数据库
-- =============================================

-- =============================================
-- 1. 用户表 (credit_user)
-- =============================================
DROP TABLE IF EXISTS `credit_user`;
CREATE TABLE `credit_user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `openid` varchar(64) NOT NULL COMMENT '微信OpenID',
  `unionid` varchar(64) DEFAULT NULL COMMENT '微信UnionID',
  `nickname` varchar(64) DEFAULT NULL COMMENT '昵称',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `gender` tinyint(1) DEFAULT '0' COMMENT '性别：0未知 1男 2女',
  `free_count` int(11) DEFAULT '3' COMMENT '免费查询次数',
  `is_vip` tinyint(1) DEFAULT '0' COMMENT '是否VIP：0否 1是',
  `vip_expire_time` datetime DEFAULT NULL COMMENT 'VIP到期时间',
  `invite_code` varchar(32) DEFAULT NULL COMMENT '我的邀请码',
  `invited_by` bigint(20) DEFAULT NULL COMMENT '邀请人ID',
  `total_commission` decimal(10,2) DEFAULT '0.00' COMMENT '累计佣金',
  `available_commission` decimal(10,2) DEFAULT '0.00' COMMENT '可用佣金',
  `frozen_commission` decimal(10,2) DEFAULT '0.00' COMMENT '冻结佣金',
  `status` tinyint(1) DEFAULT '1' COMMENT '状态：0禁用 1正常',
  `last_login_time` datetime DEFAULT NULL COMMENT '最后登录时间',
  `last_login_ip` varchar(64) DEFAULT NULL COMMENT '最后登录IP',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否删除：0否 1是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_openid` (`openid`),
  UNIQUE KEY `uk_invite_code` (`invite_code`),
  KEY `idx_phone` (`phone`),
  KEY `idx_invited_by` (`invited_by`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- =============================================
-- 2. 征信报告表 (credit_report)
-- =============================================
DROP TABLE IF EXISTS `credit_report`;
CREATE TABLE `credit_report` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  `task_id` varchar(64) NOT NULL COMMENT '任务ID',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '用户ID',
  `file_name` varchar(255) DEFAULT NULL COMMENT '文件名',
  `file_path` varchar(500) DEFAULT NULL COMMENT '文件路径',
  `file_size` bigint(20) DEFAULT NULL COMMENT '文件大小(字节)',
  `status` varchar(20) DEFAULT 'uploaded' COMMENT '状态：uploaded/processing/completed/failed',
  `credit_score` int(11) DEFAULT NULL COMMENT '信用评分',
  `risk_level` varchar(20) DEFAULT NULL COMMENT '风险等级：低风险/中风险/高风险',
  `personal_info` json DEFAULT NULL COMMENT '个人信息(JSON)',
  `credit_records` json DEFAULT NULL COMMENT '信贷记录(JSON)',
  `overdue_records` json DEFAULT NULL COMMENT '逾期记录(JSON)',
  `query_records` json DEFAULT NULL COMMENT '查询记录(JSON)',
  `public_records` json DEFAULT NULL COMMENT '公共记录(JSON)',
  `risk_tips` json DEFAULT NULL COMMENT '风险提示(JSON数组)',
  `suggestions` json DEFAULT NULL COMMENT '建议(JSON数组)',
  `error_message` varchar(500) DEFAULT NULL COMMENT '错误信息',
  `ocr_text` text COMMENT 'OCR识别原文',
  `ai_analysis` text COMMENT 'AI分析原文',
  `cost_amount` decimal(10,2) DEFAULT '0.00' COMMENT '消费金额',
  `is_free` tinyint(1) DEFAULT '0' COMMENT '是否免费：0否 1是',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否删除：0否 1是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_task_id` (`task_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='征信报告表';

-- =============================================
-- 3. 消费记录表 (credit_consume)
-- =============================================
DROP TABLE IF EXISTS `credit_consume`;
CREATE TABLE `credit_consume` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '用户ID',
  `report_id` bigint(20) unsigned DEFAULT NULL COMMENT '报告ID',
  `type` varchar(20) NOT NULL COMMENT '类型：query/recharge/vip/commission',
  `amount` decimal(10,2) NOT NULL COMMENT '金额',
  `balance_before` decimal(10,2) DEFAULT '0.00' COMMENT '变动前余额',
  `balance_after` decimal(10,2) DEFAULT '0.00' COMMENT '变动后余额',
  `free_count_before` int(11) DEFAULT '0' COMMENT '变动前免费次数',
  `free_count_after` int(11) DEFAULT '0' COMMENT '变动后免费次数',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_report_id` (`report_id`),
  KEY `idx_type` (`type`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消费记录表';

-- =============================================
-- 4. 订单表 (credit_order)
-- =============================================
DROP TABLE IF EXISTS `credit_order`;
CREATE TABLE `credit_order` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `order_no` varchar(64) NOT NULL COMMENT '订单号',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '用户ID',
  `type` varchar(20) NOT NULL COMMENT '订单类型：query/vip/recharge',
  `amount` decimal(10,2) NOT NULL COMMENT '订单金额',
  `pay_amount` decimal(10,2) DEFAULT NULL COMMENT '实付金额',
  `pay_type` varchar(20) DEFAULT NULL COMMENT '支付方式：wechat/alipay',
  `pay_time` datetime DEFAULT NULL COMMENT '支付时间',
  `pay_trade_no` varchar(64) DEFAULT NULL COMMENT '第三方交易号',
  `status` varchar(20) DEFAULT 'pending' COMMENT '状态：pending/paid/cancelled/refunded',
  `vip_days` int(11) DEFAULT NULL COMMENT 'VIP天数',
  `query_count` int(11) DEFAULT NULL COMMENT '查询次数',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否删除：0否 1是',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- =============================================
-- 5. VIP套餐表 (credit_vip_package)
-- =============================================
DROP TABLE IF EXISTS `credit_vip_package`;
CREATE TABLE `credit_vip_package` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '套餐ID',
  `name` varchar(64) NOT NULL COMMENT '套餐名称',
  `days` int(11) NOT NULL COMMENT '有效天数',
  `price` decimal(10,2) NOT NULL COMMENT '价格',
  `original_price` decimal(10,2) DEFAULT NULL COMMENT '原价',
  `query_count` int(11) DEFAULT '0' COMMENT '赠送查询次数',
  `description` varchar(500) DEFAULT NULL COMMENT '描述',
  `sort` int(11) DEFAULT '0' COMMENT '排序',
  `status` tinyint(1) DEFAULT '1' COMMENT '状态：0下架 1上架',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_deleted` tinyint(1) DEFAULT '0' COMMENT '是否删除：0否 1是',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_sort` (`sort`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='VIP套餐表';

-- =============================================
-- 6. 邀请记录表 (credit_invite)
-- =============================================
DROP TABLE IF EXISTS `credit_invite`;
CREATE TABLE `credit_invite` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '邀请人ID',
  `invite_user_id` bigint(20) unsigned NOT NULL COMMENT '被邀请人ID',
  `commission` decimal(10,2) DEFAULT '0.00' COMMENT '获得佣金',
  `status` varchar(20) DEFAULT 'pending' COMMENT '状态：pending/settled/cancelled',
  `settle_time` datetime DEFAULT NULL COMMENT '结算时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_invite_user_id` (`invite_user_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='邀请记录表';

-- =============================================
-- 7. 系统配置表 (credit_config)
-- =============================================
DROP TABLE IF EXISTS `credit_config`;
CREATE TABLE `credit_config` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `config_key` varchar(64) NOT NULL COMMENT '配置键',
  `config_value` text COMMENT '配置值',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_config_key` (`config_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- =============================================
-- 8. 提现记录表 (credit_withdraw)
-- =============================================
DROP TABLE IF EXISTS `credit_withdraw`;
CREATE TABLE `credit_withdraw` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id` bigint(20) unsigned NOT NULL COMMENT '用户ID',
  `amount` decimal(10,2) NOT NULL COMMENT '提现金额',
  `status` varchar(20) DEFAULT 'pending' COMMENT '状态：pending/success/failed',
  `real_name` varchar(64) DEFAULT NULL COMMENT '真实姓名',
  `bank_name` varchar(64) DEFAULT NULL COMMENT '银行名称',
  `bank_card` varchar(32) DEFAULT NULL COMMENT '银行卡号',
  `alipay_account` varchar(64) DEFAULT NULL COMMENT '支付宝账号',
  `wechat_account` varchar(64) DEFAULT NULL COMMENT '微信账号',
  `fail_reason` varchar(255) DEFAULT NULL COMMENT '失败原因',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `transfer_time` datetime DEFAULT NULL COMMENT '转账时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提现记录表';

-- =============================================
-- 初始化数据
-- =============================================

-- 初始化VIP套餐
INSERT INTO `credit_vip_package` (`name`, `days`, `price`, `original_price`, `query_count`, `description`, `sort`, `status`) VALUES
('月度会员', 30, 29.90, 49.00, 10, '每月10次免费查询', 1, 1),
('季度会员', 90, 79.90, 147.00, 35, '每季度35次免费查询', 2, 1),
('年度会员', 365, 199.90, 588.00, 200, '每年200次免费查询', 3, 1);

-- 初始化系统配置
INSERT INTO `credit_config` (`config_key`, `config_value`, `description`) VALUES
('query_price', '9.90', '单次查询价格'),
('free_count', '3', '新用户免费查询次数'),
('invite_commission_rate', '0.10', '邀请佣金比例'),
('min_withdraw_amount', '10.00', '最低提现金额'),
('withdraw_fee_rate', '0.00', '提现手续费比例');
