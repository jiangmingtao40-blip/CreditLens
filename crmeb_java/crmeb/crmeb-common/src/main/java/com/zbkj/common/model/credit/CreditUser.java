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
 * 征信用户实体类
 */
@Data
@EqualsAndHashCode(callSuper = false)
@TableName("credit_user")
public class CreditUser implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 微信OpenID
     */
    private String openid;

    /**
     * 微信UnionID
     */
    private String unionid;

    /**
     * 昵称
     */
    private String nickname;

    /**
     * 头像URL
     */
    private String avatar;

    /**
     * 手机号
     */
    private String phone;

    /**
     * 性别：0未知 1男 2女
     */
    private Integer gender;

    /**
     * 免费查询次数
     */
    private Integer freeCount;

    /**
     * 是否VIP：0否 1是
     */
    private Integer isVip;

    /**
     * VIP到期时间
     */
    private Date vipExpireTime;

    /**
     * 我的邀请码
     */
    private String inviteCode;

    /**
     * 邀请人ID
     */
    private Long invitedBy;

    /**
     * 累计佣金
     */
    private BigDecimal totalCommission;

    /**
     * 可用佣金
     */
    private BigDecimal availableCommission;

    /**
     * 冻结佣金
     */
    private BigDecimal frozenCommission;

    /**
     * 状态：0禁用 1正常
     */
    private Integer status;

    /**
     * 最后登录时间
     */
    private Date lastLoginTime;

    /**
     * 最后登录IP
     */
    private String lastLoginIp;

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
