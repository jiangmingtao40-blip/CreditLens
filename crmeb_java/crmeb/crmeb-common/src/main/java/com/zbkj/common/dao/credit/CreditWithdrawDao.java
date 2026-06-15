package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zbkj.common.model.credit.CreditWithdraw;
import org.apache.ibatis.annotations.Mapper;

/**
 * 提现记录DAO
 */
@Mapper
public interface CreditWithdrawDao extends BaseMapper<CreditWithdraw> {
}
