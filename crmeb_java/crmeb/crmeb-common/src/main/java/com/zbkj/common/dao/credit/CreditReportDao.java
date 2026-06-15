package com.zbkj.common.dao.credit;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.zbkj.common.model.credit.CreditReport;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 征信报告DAO
 */
@Mapper
public interface CreditReportDao extends BaseMapper<CreditReport> {

    /**
     * 根据任务ID查询报告
     */
    CreditReport selectByTaskId(@Param("taskId") String taskId);

    /**
     * 分页查询用户报告
     */
    IPage<CreditReport> selectPageByUserId(Page<CreditReport> page, @Param("userId") Long userId);

    /**
     * 统计用户报告数量
     */
    Integer countByUserId(@Param("userId") Long userId);
}
