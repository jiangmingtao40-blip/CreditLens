package com.zbkj.common.service.credit;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditVipPackageDao;
import com.zbkj.common.model.credit.CreditUser;
import com.zbkj.common.model.credit.CreditVipPackage;
import com.zbkj.common.response.credit.VipPackageResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

/**
 * VIP会员服务
 */
@Slf4j
@Service
public class CreditVipService extends ServiceImpl<CreditVipPackageDao, CreditVipPackage> {

    @Autowired
    private CreditUserService creditUserService;

    /**
     * 获取所有VIP套餐
     */
    public List<VipPackageResponse> getVipPackages() {
        List<CreditVipPackage> packages = list(new LambdaQueryWrapper<CreditVipPackage>()
                .eq(CreditVipPackage::getStatus, 1)
                .eq(CreditVipPackage::getIsDeleted, 0)
                .orderByAsc(CreditVipPackage::getSort));

        List<VipPackageResponse> responseList = new ArrayList<>();
        for (CreditVipPackage pkg : packages) {
            VipPackageResponse response = new VipPackageResponse();
            BeanUtils.copyProperties(pkg, response);
            // 季度会员设为推荐
            response.setIsRecommend(pkg.getDays() == 90);
            responseList.add(response);
        }

        return responseList;
    }

    /**
     * 购买VIP
     */
    @Transactional(rollbackFor = Exception.class)
    public boolean purchaseVip(Long userId, Long packageId) {
        CreditVipPackage vipPackage = getById(packageId);
        if (vipPackage == null || vipPackage.getStatus() != 1) {
            log.error("VIP套餐不存在或已下架: packageId={}", packageId);
            return false;
        }

        CreditUser user = creditUserService.getById(userId);
        if (user == null) {
            log.error("用户不存在: userId={}", userId);
            return false;
        }

        // 计算VIP到期时间
        Date now = new Date();
        Date vipExpireTime = user.getVipExpireTime();
        
        if (vipExpireTime == null || vipExpireTime.before(now)) {
            // 首次购买或已过期，从当前时间开始计算
            vipExpireTime = now;
        }

        Calendar calendar = Calendar.getInstance();
        calendar.setTime(vipExpireTime);
        calendar.add(Calendar.DAY_OF_MONTH, vipPackage.getDays());
        vipExpireTime = calendar.getTime();

        // 更新用户VIP信息
        user.setIsVip(1);
        user.setVipExpireTime(vipExpireTime);
        user.setFreeCount(user.getFreeCount() + vipPackage.getQueryCount());

        boolean success = creditUserService.updateById(user);
        
        if (success) {
            log.info("VIP购买成功: userId={}, packageId={}, expireTime={}", 
                    userId, packageId, vipExpireTime);
        }

        return success;
    }

    /**
     * 检查VIP是否有效
     */
    public boolean isVipValid(Long userId) {
        CreditUser user = creditUserService.getById(userId);
        if (user == null || user.getIsVip() != 1) {
            return false;
        }

        if (user.getVipExpireTime() == null) {
            return false;
        }

        return user.getVipExpireTime().after(new Date());
    }
}
