<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Header -->
		<view class="page-header">
			<text class="back-arrow" @click="goBack">←</text>
			<view class="page-title">历史记录</view>
			<view class="header-spacer"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Loading -->
			<view class="loading-state" v-if="loading">
				<view class="loading-text">加载中...</view>
			</view>
			
			<!-- Record List -->
			<view 
				class="record-card" 
				v-for="(record, index) in records" 
				:key="index"
				@click="viewRecord(record)"
			>
				<view class="left">
					<view class="record-date">{{ record.date }}</view>
					<view class="record-report">{{ record.reportType }}</view>
				</view>
				<view class="record-score" :class="{ na: !record.score }">
					{{ record.score || 'N/A' }}
				</view>
			</view>
			
			<!-- Empty State -->
			<view class="empty-state" v-if="!loading && records.length === 0">
				<view class="empty-icon">📋</view>
				<view class="empty-text">暂无历史记录</view>
				<view class="empty-hint">开始您的第一次信用分析</view>
			</view>
			
			<!-- End Hint -->
			<view class="end-hint" v-if="records.length > 0">— 已加载全部 —</view>
		</scroll-view>
	</view>
</template>

<script>
	import { getHistory } from '@/api/credit.js';

	export default {
		data() {
			return {
				records: [],
				loading: true
			}
		},
		onLoad() {
			this.loadRecords();
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			loadRecords() {
				this.loading = true;
				getHistory().then((list) => {
					this.records = (list || []).map(function(item) {
						return {
							id: item.id,
							taskId: item.taskId,
							date: item.createTime || item.date || '',
							reportType: item.fileName || '个人征信报告',
							score: item.creditScore
						};
					});
				}).catch(function(err) {
					console.error('加载历史记录失败:', err);
					uni.showToast({ title: '加载失败', icon: 'none' });
				}).finally(() => {
					this.loading = false;
				});
			},
			viewRecord(record) {
				uni.navigateTo({
					url: '/pages/credit/result?taskId=' + record.taskId
				});
			}
		}
	}
</script>

<style lang="scss" scoped>
page {
	background: #F8FAFC;
}

.page {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: #F8FAFC;
}

/* Status Bar */
.status-bar {
	display: flex;
	align-items: center;
	height: 62rpx;
	padding: 0 48rpx;
	flex-shrink: 0;
	
	.time {
		font-size: 28rpx;
		font-weight: 600;
		color: #1E293B;
	}
	
	.spacer {
		flex: 1;
	}
	
	.battery {
		width: 48rpx;
		height: 24rpx;
		background: #CBD5E1;
		border-radius: 6rpx;
	}
}

/* Page Header */
.page-header {
	display: flex;
	align-items: center;
	height: 88rpx;
	padding: 0 24rpx;
	gap: 24rpx;
}

.back-arrow {
	font-size: 44rpx;
	font-weight: 600;
	color: #1E293B;
	font-family: 'IBM Plex Sans', sans-serif;
	line-height: 1;
}

.page-title {
	flex: 1;
	font-size: 36rpx;
	font-weight: 700;
	color: #1E293B;
	text-align: center;
}

.header-spacer {
	width: 48rpx;
}

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

/* Loading State */
.loading-state {
	display: flex;
	justify-content: center;
	padding: 80rpx 0;
}

.loading-text {
	font-size: 28rpx;
	color: #94A3B8;
}

/* Record Card */
.record-card {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 32rpx 28rpx;
	gap: 24rpx;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.record-card .left {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.record-date {
	font-size: 28rpx;
	font-weight: 600;
	color: #1E293B;
}

.record-report {
	font-size: 22rpx;
	color: #94A3B8;
}

.record-score {
	font-family: 'IBM Plex Sans', sans-serif;
	font-size: 40rpx;
	font-weight: 700;
	color: #6366F1;
	
	&.na {
		color: #94A3B8;
	}
}

/* Empty State */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 120rpx 0;
}

.empty-icon {
	font-size: 96rpx;
	margin-bottom: 32rpx;
}

.empty-text {
	font-size: 32rpx;
	font-weight: 600;
	color: #64748B;
	margin-bottom: 16rpx;
}

.empty-hint {
	font-size: 26rpx;
	color: #94A3B8;
}

/* End Hint */
.end-hint {
	font-size: 24rpx;
	color: #94A3B8;
	text-align: center;
	padding: 32rpx 0;
}
</style>
