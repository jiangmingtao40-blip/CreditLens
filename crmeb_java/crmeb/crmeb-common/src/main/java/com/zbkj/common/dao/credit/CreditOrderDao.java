package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zbkj.common.model.credit.CreditOrder;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 订单DAO
 */
@Mapper
public interface CreditOrderDao extends BaseMapper<CreditOrder> {

    /**
     * 根据订单号查询订单
     */
    CreditOrder selectByOrderNo(@Param("orderNo") String orderNo);
}
