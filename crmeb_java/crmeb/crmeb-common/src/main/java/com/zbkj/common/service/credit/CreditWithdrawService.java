package com.zbkj.common.service.credit;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditWithdrawDao;
import com.zbkj.common.model.credit.CreditUser;
import com.zbkj.common.model.credit.CreditWithdraw;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Date;
import java.util.Map;

/**
 * 征信提现服务
 */
@Slf4j
@Service
public class CreditWithdrawService extends ServiceImpl<CreditWithdrawDao, CreditWithdraw> {

    @Autowired
    private CreditUserService creditUserService;

    /**
     * 申请提现
     */
    @Transactional(rollbackFor = Exception.class)
    public boolean applyWithdraw(Long userId, BigDecimal amount, Map<String, Object> accountInfo) {
        log.info("申请提现: userId={}, amount={}", userId, amount);

        CreditUser user = creditUserService.getById(userId);
        if (user == null) {
            log.error("用户不存在: userId={}", userId);
            return false;
        }

        // 检查可用佣金
        if (user.getAvailableCommission().compareTo(amount) < 0) {
            log.error("可用佣金不足: available={}, request={}", user.getAvailableCommission(), amount);
            return false;
        }

        // 创建提现记录
        CreditWithdraw withdraw = new CreditWithdraw();
        withdraw.setUserId(userId);
        withdraw.setAmount(amount);
        withdraw.setStatus("pending"); // 审核中
        
        // 设置账户信息
        String accountType = (String) accountInfo.get("accountType");
        if ("wechat".equals(accountType)) {
            withdraw.setWechatAccount((String) accountInfo.get("accountNo"));
        } else if ("alipay".equals(accountType)) {
            withdraw.setAlipayAccount((String) accountInfo.get("accountNo"));
        } else if ("bank".equals(accountType)) {
            withdraw.setBankName((String) accountInfo.get("bankName"));
            withdraw.setBankCard((String) accountInfo.get("accountNo"));
        }
        withdraw.setRealName((String) accountInfo.get("accountName"));
        withdraw.setCreateTime(new Date());

        save(withdraw);

        // 冻结佣金
        user.setAvailableCommission(user.getAvailableCommission().subtract(amount));
        user.setFrozenCommission(user.getFrozenCommission().add(amount));
        creditUserService.updateById(user);

        return true;
    }
}
