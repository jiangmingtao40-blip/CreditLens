<template>
	<view class="info-card">
		<view class="card-header">
			<text class="card-icon">{{ icon }}</text>
			<text class="card-title">{{ title }}</text>
		</view>
		<view class="card-body">
			<slot></slot>
		</view>
	</view>
</template>

<script>
	export default {
		name: 'CreditInfoCard',
		props: {
			title: {
				type: String,
				default: ''
			},
			icon: {
				type: String,
				default: '📋'
			}
		}
	}
</script>

<style scoped>
	.info-card {
		background: #fff;
		border-radius: 16rpx;
		padding: 24rpx;
		margin-bottom: 20rpx;
		box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
	}

	.card-header {
		display: flex;
		align-items: center;
		margin-bottom: 20rpx;
		padding-bottom: 16rpx;
		border-bottom: 1rpx solid #f0f0f0;
	}

	.card-icon {
		font-size: 32rpx;
		margin-right: 12rpx;
	}

	.card-title {
		font-size: 28rpx;
		font-weight: bold;
		color: #333;
	}

	.card-body {
		font-size: 26rpx;
		color: #666;
		line-height: 1.8;
	}
</style>
