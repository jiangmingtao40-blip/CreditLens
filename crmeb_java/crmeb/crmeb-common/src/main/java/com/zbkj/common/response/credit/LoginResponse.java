package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;

/**
 * 登录响应
 */
@Data
public class LoginResponse implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * 用户ID
     */
    private Long userId;

    /**
     * Token
     */
    private String token;

    /**
     * 昵称
     */
    private String nickname;

    /**
     * 头像
     */
    private String avatar;

    /**
     * 手机号
     */
    private String phone;

    /**
     * 免费查询次数
     */
    private Integer freeCount;

    /**
     * 是否VIP
     */
    private Boolean isVip;

    /**
     * VIP到期时间
     */
    private Date vipExpireTime;

    /**
     * 我的邀请码
     */
    private String inviteCode;

    /**
     * 累计佣金
     */
    private BigDecimal totalCommission;

    /**
     * 可用佣金
     */
    private BigDecimal availableCommission;

    /**
     * 是否新用户
     */
    private Boolean isNew;
}
