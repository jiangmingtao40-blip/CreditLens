package com.zbkj.common.service.credit;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditInviteDao;
import com.zbkj.common.model.credit.CreditInvite;
import com.zbkj.common.model.credit.CreditUser;
import com.zbkj.common.response.credit.InviteListResponse;
import com.zbkj.common.response.credit.InviteStatsResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * 征信邀请服务
 */
@Slf4j
@Service
public class CreditInviteService extends ServiceImpl<CreditInviteDao, CreditInvite> {

    @Autowired
    private CreditUserService creditUserService;

    /**
     * 获取邀请统计
     */
    public InviteStatsResponse getInviteStats(Long userId) {
        CreditUser user = creditUserService.getById(userId);
        
        InviteStatsResponse response = new InviteStatsResponse();
        response.setTotalInvited(count(new LambdaQueryWrapper<CreditInvite>()
                .eq(CreditInvite::getUserId, userId)));
        response.setTodayInvited(count(new LambdaQueryWrapper<CreditInvite>()
                .eq(CreditInvite::getUserId, userId)
                .ge(CreditInvite::getCreateTime, getTodayStart())));
        response.setTotalCommission(user != null ? user.getTotalCommission() : BigDecimal.ZERO);
        response.setAvailableCommission(user != null ? user.getAvailableCommission() : BigDecimal.ZERO);

        return response;
    }

    /**
     * 获取邀请列表
     */
    public InviteListResponse getInviteList(Long userId, Integer page, Integer limit) {
        Page<CreditInvite> pageQuery = new Page<>(page, limit);
        
        Page<CreditInvite> resultPage = page(pageQuery, new LambdaQueryWrapper<CreditInvite>()
                .eq(CreditInvite::getUserId, userId)
                .orderByDesc(CreditInvite::getCreateTime));

        List<InviteListResponse.InviteItem> records = new ArrayList<>();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        
        for (CreditInvite invite : resultPage.getRecords()) {
            CreditUser invitedUser = creditUserService.getById(invite.getInviteUserId());
            
            InviteListResponse.InviteItem item = new InviteListResponse.InviteItem();
            item.setId(invite.getId());
            item.setNickname(invitedUser != null ? invitedUser.getNickname() : "未知");
            item.setAvatar(invitedUser != null ? invitedUser.getAvatar() : "");
            item.setPhone(invitedUser != null ? invitedUser.getPhone() : "");
            item.setCommission(invite.getCommission());
            item.setInviteTime(sdf.format(invite.getCreateTime()));
            
            records.add(item);
        }

        InviteListResponse response = new InviteListResponse();
        response.setRecords(records);
        response.setTotal((int) resultPage.getTotal());
        response.setSize((int) resultPage.getSize());
        response.setCurrent((int) resultPage.getCurrent());

        return response;
    }

    /**
     * 获取今天开始时间
     */
    private Date getTodayStart() {
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
            return sdf.parse(sdf.format(new Date()));
        } catch (Exception e) {
            return new Date();
        }
    }
}
