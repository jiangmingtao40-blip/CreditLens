package com.zbkj.common.model.credit;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 提现记录实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_withdraw")
public class CreditWithdraw implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("user_id")
    private Long userId; // 用户ID
    private BigDecimal amount; // 提现金额
    private String status; // 状态
    @TableField("real_name")
    private String realName; // 真实姓名
    @TableField("bank_name")
    private String bankName; // 银行名称
    @TableField("bank_card")
    private String bankCard; // 银行卡号
    @TableField("alipay_account")
    private String alipayAccount; // 支付宝账号
    @TableField("wechat_account")
    private String wechatAccount; // 微信账号
    @TableField("fail_reason")
    private String failReason; // 失败原因
    @TableField("audit_time")
    private Date auditTime; // 审核时间
    @TableField("transfer_time")
    private Date transferTime; // 打款时间
    @TableField("create_time")
    private Date createTime;
    @TableField("update_time")
    private Date updateTime;
}
