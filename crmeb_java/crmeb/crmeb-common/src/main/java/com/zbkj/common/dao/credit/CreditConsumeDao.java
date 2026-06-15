package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zbkj.common.model.credit.CreditConsume;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 消费记录DAO
 */
@Mapper
public interface CreditConsumeDao extends BaseMapper<CreditConsume> {

    /**
     * 分页查询用户消费记录
     */
    IPage<CreditConsume> selectPageByUserId(Page<CreditConsume> page, @Param("userId") Long userId);
}
