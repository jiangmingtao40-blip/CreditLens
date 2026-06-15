<template>
	<view class="page">
		<!-- Status Bar -->
		<view class="status-bar">
			<text class="time">9:41</text>
			<view class="spacer"></view>
			<view class="battery"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Page Header -->
			<view class="page-header">
				<view class="page-title left">历史记录</view>
			</view>
			
			<!-- Record List -->
			<view class="record-list">
				<view class="record-card" @click="viewRecord">
					<view class="left">
						<view class="record-date">2024-03-15 &nbsp; 14:30</view>
						<view class="record-report">个人信用报告 · 简版</view>
					</view>
					<view class="record-score">782</view>
				</view>
				
				<view class="record-card" @click="viewRecord">
					<view class="left">
						<view class="record-date">2024-03-01 &nbsp; 10:15</view>
						<view class="record-report">个人信用报告 · 详细版</view>
					</view>
					<view class="record-score">756</view>
				</view>
				
				<view class="record-card" @click="viewRecord">
					<view class="left">
						<view class="record-date">2024-02-20 &nbsp; 09:45</view>
						<view class="record-report">企业信用报告</view>
					</view>
					<view class="record-score na">—</view>
				</view>
			</view>
			
			<!-- End Hint -->
			<view class="end-hint">—&nbsp;&nbsp;已加载全部记录&nbsp;&nbsp;—</view>
			
			<!-- Bottom Spacing -->
			<view class="bottom-spacing"></view>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="1" @change="onTabChange"></TabBar>
	</view>
</template>

<script setup lang="ts">
import TabBar from '@/components/TabBar/index.vue'

const viewRecord = () => {
	uni.navigateTo({ url: '/pages/result/result' })
}

const onTabChange = (index: number) => {
	const routes = [
		'/pages/index/index',
		'/pages/records/records',
		'/pages/upload/upload',
		'/pages/result/result',
		'/pages/profile/profile'
	]
	if (routes[index]) {
		uni.navigateTo({ url: routes[index] })
	}
}
</script>

<style lang="scss" scoped>
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
	background: #F8FAFC;
	
	.time {
		font-family: 'IBM Plex Sans', sans-serif;
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

/* Content */
.content {
	flex: 1;
	padding: 20rpx;
	overflow-y: auto;
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

/* Page Header */
.page-header {
	height: 44rpx;
	
	.page-title {
		font-size: 36rpx;
		font-weight: 700;
		color: #1E293B;
		
		&.left {
			text-align: left;
		}
	}
}

/* Record Cards */
.record-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.record-card {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 28rpx;
	padding: 32rpx 28rpx;
	gap: 24rpx;
	box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.04);
	
	.left {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 8rpx;
	}
	
	.record-date {
		font-size: 26rpx;
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
}

/* End Hint */
.end-hint {
	font-size: 24rpx;
	color: #94A3B8;
	text-align: center;
	padding: 16rpx 0;
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>
