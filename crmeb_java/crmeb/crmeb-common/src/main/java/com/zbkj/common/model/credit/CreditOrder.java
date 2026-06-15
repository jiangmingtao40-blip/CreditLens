package com.zbkj.common.model.credit;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 订单实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_order")
public class CreditOrder implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 订单ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 订单号
     */
    private String orderNo;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 订单类型：query/vip/recharge
     */
    private String type;

    /**
     * 订单金额
     */
    private BigDecimal amount;

    /**
     * 实付金额
     */
    private BigDecimal payAmount;

    /**
     * 支付方式：wechat/alipay
     */
    private String payType;

    /**
     * 支付时间
     */
    private Date payTime;

    /**
     * 第三方交易号
     */
    private String payTradeNo;

    /**
     * 状态：pending/paid/cancelled/refunded
     */
    private String status;

    /**
     * VIP天数
     */
    private Integer vipDays;

    /**
     * 查询次数
     */
    private Integer queryCount;

    /**
     * 备注
     */
    private String remark;

    /**
     * 创建时间
     */
    private Date createTime;

    /**
     * 更新时间
     */
    private Date updateTime;

    /**
     * 是否删除：0否 1是
     */
    private Integer isDeleted;
}
