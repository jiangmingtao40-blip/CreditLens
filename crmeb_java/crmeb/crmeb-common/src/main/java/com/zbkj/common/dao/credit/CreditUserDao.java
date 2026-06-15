package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zbkj.common.model.credit.CreditUser;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 征信用户DAO
 */
@Mapper
public interface CreditUserDao extends BaseMapper<CreditUser> {

    /**
     * 根据OpenID查询用户
     */
    CreditUser selectByOpenid(@Param("openid") String openid);

    /**
     * 根据邀请码查询用户
     */
    CreditUser selectByInviteCode(@Param("inviteCode") String inviteCode);
}
