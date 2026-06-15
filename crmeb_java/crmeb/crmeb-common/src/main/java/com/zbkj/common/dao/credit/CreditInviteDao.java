package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zbkj.common.model.credit.CreditInvite;
import org.apache.ibatis.annotations.Mapper;

/**
 * 邀请记录DAO
 */
@Mapper
public interface CreditInviteDao extends BaseMapper<CreditInvite> {
}
