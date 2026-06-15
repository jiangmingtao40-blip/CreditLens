package com.zbkj.common.response.credit;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.util.List;

/**
 * 邀请列表响应
 */
@Data
public class InviteListResponse implements Serializable {
    private static final long serialVersionUID = 1L;

    private List<InviteItem> records;
    private Integer total;
    private Integer size;
    private Integer current;

    @Data
    public static class InviteItem {
        private Long id;
        private String nickname;
        private String avatar;
        private String phone;
        private BigDecimal commission; // 获得的佣金
        private String inviteTime; // 邀请时间
    }
}
