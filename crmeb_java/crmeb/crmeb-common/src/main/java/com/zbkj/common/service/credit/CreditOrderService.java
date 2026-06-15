package com.zbkj.common.service.credit;

import cn.hutool.core.util.IdUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.zbkj.common.dao.credit.CreditOrderDao;
import com.zbkj.common.model.credit.CreditOrder;
import com.zbkj.common.response.PayCreateResponse;
import com.zbkj.common.response.PayStatusResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.Date;

/**
 * 征信订单服务
 */
@Slf4j
@Service
public class CreditOrderService extends ServiceImpl<CreditOrderDao, CreditOrder> {

    /**
     * 创建订单
     */
    @Transactional(rollbackFor = Exception.class)
    public PayCreateResponse createOrder(Long userId, String type, BigDecimal amount) {
        log.info("创建订单: userId={}, type={}, amount={}", userId, type, amount);

        CreditOrder order = new CreditOrder();
        order.setOrderNo(generateOrderNo());
        order.setUserId(userId);
        order.setType(type);
        order.setAmount(amount);
        order.setStatus("pending"); // 待支付
        order.setCreateTime(new Date());
        order.setUpdateTime(new Date());
        order.setIsDeleted(0);

        save(order);

        PayCreateResponse response = new PayCreateResponse();
        response.setOrderId(order.getOrderNo());
        response.setAmount(amount);
        response.setPayUrl(""); // 实际应该生成支付URL
        response.setQrCode(""); // 实际应该生成二维码
        response.setExpireTime(System.currentTimeMillis() + 30 * 60 * 1000L); // 30分钟过期

        return response;
    }

    /**
     * 获取订单状态
     */
    public PayStatusResponse getOrderStatus(String orderId) {
        CreditOrder order = getOne(new LambdaQueryWrapper<CreditOrder>()
                .eq(CreditOrder::getOrderNo, orderId)
                .eq(CreditOrder::getIsDeleted, 0));

        if (order == null) {
            return null;
        }

        PayStatusResponse response = new PayStatusResponse();
        response.setOrderId(order.getOrderNo());
        response.setAmount(order.getAmount());
        
        String status = order.getStatus();
        if ("pending".equals(status)) {
            response.setStatus(0);
            response.setStatusText("待支付");
        } else if ("paid".equals(status)) {
            response.setStatus(1);
            response.setStatusText("支付成功");
        } else if ("cancelled".equals(status)) {
            response.setStatus(2);
            response.setStatusText("已取消");
        } else if ("refunded".equals(status)) {
            response.setStatus(3);
            response.setStatusText("已退款");
        } else {
            response.setStatus(-1);
            response.setStatusText("未知");
        }

        return response;
    }

    /**
     * 生成订单号
     */
    private String generateOrderNo() {
        return "CR" + System.currentTimeMillis() + IdUtil.simpleUUID().substring(0, 8).toUpperCase();
    }
}
