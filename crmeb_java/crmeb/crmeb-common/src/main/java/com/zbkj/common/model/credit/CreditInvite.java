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
 * 邀请记录实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_invite")
public class CreditInvite implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @TableField("user_id")
    private Long userId; // 用户ID（邀请人）
    @TableField("invite_user_id")
    private Long inviteUserId; // 被邀请人ID
    private BigDecimal commission; // 获得佣金
    private String status; // 状态
    @TableField("settle_time")
    private Date settleTime; // 结算时间
    @TableField("create_time")
    private Date createTime;
}
