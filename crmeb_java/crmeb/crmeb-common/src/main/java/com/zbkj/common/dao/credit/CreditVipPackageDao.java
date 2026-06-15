package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.zbkj.common.model.credit.CreditVipPackage;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * VIP套餐DAO
 */
@Mapper
public interface CreditVipPackageDao extends BaseMapper<CreditVipPackage> {

    /**
     * 查询所有上架套餐
     */
    List<CreditVipPackage> selectAllActive();
}
