package com.zbkj.common.service.credit;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditConsumeDao;
import com.zbkj.common.model.credit.CreditConsume;
import com.zbkj.common.response.credit.ConsumeListResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 消费记录服务
 */
@Slf4j
@Service
public class CreditConsumeService extends ServiceImpl<CreditConsumeDao, CreditConsume> {

    private static final Map<String, String> TYPE_DESC_MAP = new HashMap<>();

    static {
        TYPE_DESC_MAP.put("query", "查询消费");
        TYPE_DESC_MAP.put("recharge", "充值");
        TYPE_DESC_MAP.put("vip", "VIP会员");
        TYPE_DESC_MAP.put("commission", "佣金收入");
    }

    /**
     * 分页查询用户消费记录
     */
    public IPage<ConsumeListResponse> getUserConsumeList(Long userId, Integer page, Integer limit) {
        Page<CreditConsume> pageParam = new Page<>(page, limit);
        IPage<CreditConsume> consumePage = baseMapper.selectPageByUserId(pageParam, userId);

        // 转换为响应对象
        IPage<ConsumeListResponse> responsePage = new Page<>(page, limit);
        responsePage.setTotal(consumePage.getTotal());
        responsePage.setPages(consumePage.getPages());

        List<ConsumeListResponse> records = new ArrayList<>();
        for (CreditConsume consume : consumePage.getRecords()) {
            ConsumeListResponse response = new ConsumeListResponse();
            BeanUtils.copyProperties(consume, response);
            response.setTypeDesc(TYPE_DESC_MAP.getOrDefault(consume.getType(), consume.getType()));
            records.add(response);
        }
        responsePage.setRecords(records);

        return responsePage;
    }

    /**
     * 创建消费记录
     */
    public boolean createConsumeRecord(Long userId, Long reportId, String type, 
                                       java.math.BigDecimal amount, String description) {
        CreditConsume consume = new CreditConsume();
        consume.setUserId(userId);
        consume.setReportId(reportId);
        consume.setType(type);
        consume.setAmount(amount);
        consume.setDescription(description);
        consume.setCreateTime(new java.util.Date());
        return save(consume);
    }
}
