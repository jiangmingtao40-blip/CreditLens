<template>
	<view class="page">
		<!-- 顶部导航 -->
		<view class="nav-bar">
			<view class="nav-back" @click="goBack">
				<view class="nav-back-icon">&#8592;</view>
			</view>
			<text class="nav-title">推广佣金</text>
			<view class="nav-right"></view>
		</view>

		<!-- 概览卡片 -->
		<view class="overview-section">
			<view class="overview-card">
				<view class="overview-header">
					<view class="overview-icon-wrap">
						<text class="overview-icon">&#128176;</text>
					</view>
					<text class="overview-title">我的佣金</text>
				</view>
				<view class="overview-row">
					<view class="overview-item">
						<view class="ov-value-wrap">
							<text class="ov-symbol">¥</text>
							<text class="ov-value">{{data.total_commission || 0}}</text>
						</view>
						<text class="ov-label">累计佣金</text>
					</view>
					<view class="overview-divider"></view>
					<view class="overview-item">
						<view class="ov-value-wrap">
							<text class="ov-symbol">¥</text>
							<text class="ov-value green">{{data.available_commission || 0}}</text>
						</view>
						<text class="ov-label">可提现</text>
					</view>
					<view class="overview-divider"></view>
					<view class="overview-item">
						<view class="ov-value-wrap">
							<text class="ov-value">{{data.total_count || 0}}</text>
							<text class="ov-unit">人</text>
						</view>
						<text class="ov-label">推荐人数</text>
					</view>
				</view>
				<button class="btn-withdraw" :disabled="(data.available_commission || 0) <= 0" @click="withdraw">
					<text class="btn-icon">&#128176;</text>
					<text class="btn-text">立即提现</text>
				</button>
			</view>
		</view>

		<!-- 分享区域 -->
		<view class="share-card">
			<view class="share-header">
				<view class="share-icon-wrap">
					<text class="share-icon">&#128227;</text>
				</view>
				<view class="share-text">
					<text class="share-title">邀请好友查询，赚取佣金</text>
					<text class="share-desc">每成功邀请一位好友付费查询，即可获得 ¥{{data.commission_rate || 9.9}} 佣金</text>
				</view>
			</view>
			<view class="share-row">
				<view class="share-link-box">
					<text class="share-link-text">{{shareLink}}</text>
					<view class="copy-btn" @click="copyLink">
						<text class="copy-icon">&#128203;</text>
					</view>
				</view>
			</view>
			<button class="btn-share" open-type="share">
				<text class="btn-icon">&#128227;</text>
				<text class="btn-text">邀请好友</text>
			</button>
		</view>

		<!-- 佣金记录 -->
		<view class="records-section">
			<view class="section-header">
				<text class="section-title">佣金记录</text>
				<text class="section-count">{{data.records && data.records.length || 0}} 条</text>
			</view>
			<view class="record-list" v-if="data.records && data.records.length">
				<view class="record-item" v-for="(item, idx) in data.records" :key="idx">
					<view class="record-left">
						<view class="record-icon" :class="item.status === '已到账' ? 'icon-success' : 'icon-pending'">
							<text>{{item.status === '已到账' ? '&#10003;' : '&#128337;'}}</text>
						</view>
						<view class="record-info">
							<text class="rec-type">{{item.type || '推荐奖励'}}</text>
							<text class="rec-time">{{item.time || '--'}}</text>
						</view>
					</view>
					<view class="record-right">
						<text class="rec-amount">+¥{{item.amount || 0}}</text>
						<text class="rec-status" :class="item.status === '已到账' ? 'status-ok' : 'status-pending'">{{item.status || '--'}}</text>
					</view>
				</view>
			</view>
			<view class="empty-block" v-else>
				<view class="empty-icon-wrap">
					<text class="empty-icon">&#128203;</text>
				</view>
				<text class="empty-text">暂无佣金记录，快去邀请好友吧</text>
			</view>
		</view>
	</view>
</template>

<script>
	import { getCommission, getShareInfo } from '@/api/credit.js';

	export default {
		data() {
			return {
				data: {},
				shareLink: ''
			}
		},
		onLoad() {
			this.loadData();
		},
		onShareAppMessage() {
			return {
				title: '免费查询你的征信报告！AI 智能分析',
				path: '/pages/credit/index?share_code=SHARE_ABC123',
				imageUrl: ''
			};
		},
		methods: {
			async loadData() {
				try {
					var comm = await getCommission().catch(function() { return {}; });
					var share = await getShareInfo().catch(function() { return {}; });
					this.data = comm || {};
					this.shareLink = (share && share.share_link) || 'https://example.com/credit?share=ABC';
				} catch (e) {}
			},
			copyLink() {
				var self = this;
				uni.setClipboardData({
					data: self.shareLink,
					success: function() {
						uni.showToast({ title: '链接已复制', icon: 'success' });
					}
				});
			},
			withdraw() {
				uni.showToast({ title: '提现功能开发中', icon: 'none' });
			},
			goBack() {
				uni.navigateBack();
			}
		}
	};
</script>

<style scoped>
.page { min-height: 100vh; background: linear-gradient(180deg, #f0f4f8 0%, #fafbfc 100%); padding-bottom: 40rpx; }

/* 顶部导航 */
.nav-bar {
	display: flex; align-items: center; justify-content: space-between;
	padding: calc(var(--status-bar-height, 44px) + 24rpx) 24rpx 28rpx;
	background: linear-gradient(145deg, #f59e0b 0%, #ef4444 50%, #dc2626 100%);
}
.nav-back, .nav-right {
	width: 72rpx; height: 72rpx;
	display: flex; align-items: center; justify-content: center;
}
.nav-back-icon { font-size: 36rpx; color: #fff; }
.nav-title { font-size: 34rpx; font-weight: 700; color: #fff; letter-spacing: 2rpx; }

/* 概览卡片 */
.overview-section { padding: 0 30rpx; margin-top: -20rpx; }
.overview-card {
	background: #fff; border-radius: 28rpx;
	padding: 36rpx;
	box-shadow: 0 12rpx 40rpx rgba(0,0,0,0.08);
	position: relative; z-index: 2;
}
.overview-header {
	display: flex; align-items: center; margin-bottom: 32rpx;
}
.overview-icon-wrap {
	width: 72rpx; height: 72rpx; border-radius: 20rpx;
	background: linear-gradient(135deg, #ff9800, #f44336);
	display: flex; align-items: center; justify-content: center;
	margin-right: 18rpx;
}
.overview-icon { font-size: 36rpx; color: #fff; }
.overview-title { font-size: 32rpx; font-weight: 800; color: #333; }

.overview-row {
	display: flex; align-items: center; justify-content: space-around;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #f5f7fa;
	margin-bottom: 24rpx;
}
.overview-item {
	flex: 1; display: flex; flex-direction: column; align-items: center;
}
.ov-value-wrap { display: flex; align-items: baseline; }
.ov-symbol { font-size: 28rpx; font-weight: 700; color: #f44336; }
.ov-value { font-size: 48rpx; font-weight: 900; color: #f44336; line-height: 1; }
.ov-value.green { color: #00c853; }
.ov-unit { font-size: 28rpx; color: #666; margin-left: 6rpx; }
.ov-label { font-size: 24rpx; color: #999; margin-top: 8rpx; }
.overview-divider {
	width: 2rpx; height: 60rpx;
	background: linear-gradient(180deg, #e0e0e0 0%, #f5f5f5 100%);
}

.btn-withdraw {
	width: 100%; height: 92rpx; border-radius: 46rpx;
	font-size: 30rpx; font-weight: 700; color: #fff;
	background: linear-gradient(145deg, #ff9800, #f44336);
	display: flex; align-items: center; justify-content: center;
	border: none;
	box-shadow: 0 8rpx 24rpx rgba(255,152,0,0.4);
	transition: all 0.3s;
}
.btn-withdraw:disabled {
	opacity: 0.4;
	box-shadow: none;
}
.btn-withdraw::after { border: none; }
.btn-withdraw:active:not(:disabled) { transform: scale(0.98); }
.btn-withdraw .btn-icon { font-size: 30rpx; margin-right: 10rpx; }

/* 分享卡片 */
.share-card {
	margin: 24rpx 30rpx; background: #fff; border-radius: 24rpx;
	padding: 32rpx; box-shadow: 0 6rpx 24rpx rgba(0,0,0,0.05);
}
.share-header {
	display: flex; align-items: flex-start; margin-bottom: 24rpx;
}
.share-icon-wrap {
	width: 64rpx; height: 64rpx; border-radius: 18rpx;
	background: linear-gradient(135deg, #667eea, #764ba2);
	display: flex; align-items: center; justify-content: center;
	margin-right: 18rpx; flex-shrink: 0;
}
.share-icon { font-size: 32rpx; color: #fff; }
.share-title {
	font-size: 30rpx; font-weight: 700; color: #333;
	display: block; margin-bottom: 8rpx;
}
.share-desc { font-size: 26rpx; color: #999; }

.share-row { margin-bottom: 20rpx; }
.share-link-box {
	display: flex; align-items: center; justify-content: space-between;
	background: #f8fafc; border-radius: 16rpx;
	padding: 20rpx 24rpx;
	border: 2rpx dashed #e0e0e0;
}
.share-link-text {
	flex: 1; font-size: 26rpx; color: #666;
	white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.copy-btn {
	width: 56rpx; height: 56rpx; border-radius: 50%;
	background: #667eea; display: flex; align-items: center; justify-content: center;
	margin-left: 16rpx;
}
.copy-icon { font-size: 26rpx; color: #fff; }

.btn-share {
	width: 100%; height: 92rpx; border-radius: 46rpx;
	font-size: 30rpx; font-weight: 700; color: #fff;
	background: linear-gradient(145deg, #667eea, #764ba2);
	display: flex; align-items: center; justify-content: center;
	border: none;
	box-shadow: 0 8rpx 24rpx rgba(102,126,234,0.4);
	transition: all 0.3s;
}
.btn-share::after { border: none; }
.btn-share:active { transform: scale(0.98); }
.btn-share .btn-icon { font-size: 30rpx; margin-right: 10rpx; }

/* 佣金记录 */
.records-section { padding: 0 30rpx; }
.section-header {
	display: flex; justify-content: space-between; align-items: center;
	margin-bottom: 20rpx;
}
.section-title { font-size: 32rpx; font-weight: 800; color: #333; }
.section-count { font-size: 26rpx; color: #999; }

.record-item {
	display: flex; justify-content: space-between; align-items: center;
	background: #fff; border-radius: 20rpx;
	padding: 24rpx; margin-bottom: 16rpx;
	box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.04);
	transition: all 0.2s;
}
.record-item:active { transform: scale(0.98); }
.record-left { display: flex; align-items: center; flex: 1; }
.record-icon {
	width: 48rpx; height: 48rpx; border-radius: 50%;
	display: flex; align-items: center; justify-content: center;
	margin-right: 18rpx;
	font-size: 24rpx;
}
.icon-success { background: #e8f5e9; color: #00c853; }
.icon-pending { background: #fff3e0; color: #ff9800; }
.record-info { flex: 1; }
.rec-type {
	font-size: 28rpx; font-weight: 600; color: #333;
	display: block; margin-bottom: 6rpx;
}
.rec-time { font-size: 24rpx; color: #999; }

.record-right { text-align: right; }
.rec-amount {
	font-size: 32rpx; font-weight: 800; color: #f44336;
	display: block; margin-bottom: 6rpx;
}
.rec-status {
	font-size: 24rpx; display: inline-block;
	padding: 6rpx 16rpx; border-radius: 16rpx;
}
.status-ok { background: #e8f5e9; color: #00c853; }
.status-pending { background: #fff3e0; color: #ff9800; }

/* 空状态 */
.empty-block {
	display: flex; flex-direction: column; align-items: center;
	padding: 60rpx 0;
}
.empty-icon-wrap {
	width: 100rpx; height: 100rpx; border-radius: 50%;
	background: #f0f2f5; display: flex; align-items: center; justify-content: center;
	margin-bottom: 20rpx;
}
.empty-icon { font-size: 48rpx; color: #ccc; }
.empty-text { font-size: 28rpx; color: #999; }
</style>