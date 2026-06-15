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
 * 消费记录实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_consume")
public class CreditConsume implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 记录ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * 报告ID
     */
    private Long reportId;

    /**
     * 类型：query/recharge/vip/commission
     */
    private String type;

    /**
     * 金额
     */
    private BigDecimal amount;

    /**
     * 变动前余额
     */
    private BigDecimal balanceBefore;

    /**
     * 变动后余额
     */
    private BigDecimal balanceAfter;

    /**
     * 变动前免费次数
     */
    private Integer freeCountBefore;

    /**
     * 变动后免费次数
     */
    private Integer freeCountAfter;

    /**
     * 描述
     */
    private String description;

    /**
     * 备注
     */
    private String remark;

    /**
     * 创建时间
     */
    private Date createTime;
}
