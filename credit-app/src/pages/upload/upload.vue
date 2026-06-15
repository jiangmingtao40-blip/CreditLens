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
				<text class="back-arrow" @click="goBack">←</text>
				<view class="page-title">上传征信报告</view>
				<view class="header-spacer"></view>
			</view>
			
			<!-- Upload Zone -->
			<view class="upload-zone" @click="chooseImage">
				<svg class="upload-icon" viewBox="0 0 48 48">
					<path d="M16 8h16v24H16z" stroke="#6366F1" stroke-width="2" fill="none"/>
					<path d="M8 32h32v8H8z" stroke="#6366F1" stroke-width="2" fill="none"/>
				</svg>
				<view class="upload-hint">{{ uploadHint }}</view>
				<view class="upload-sub">支持 JPG / PNG / PDF 格式，最大 20MB</view>
			</view>
			
			<!-- Action Buttons -->
			<view class="action-row">
				<button class="action-btn outline" @click="takePhoto">
					<svg viewBox="0 0 20 20">
						<rect x="1" y="5" width="12" height="12" rx="1" stroke="#6366F1" stroke-width="1.5" fill="none"/>
						<path d="M16 7l3-3v3h-3z" stroke="#6366F1" stroke-width="1.5" fill="none" stroke-linecap="round"/>
					</svg>
					拍照
				</button>
				<button class="action-btn filled" @click="chooseImage">
					<svg viewBox="0 0 20 20">
						<rect x="2" y="2" width="16" height="16" rx="2" stroke="white" stroke-width="1.5" fill="none"/>
						<circle cx="7" cy="7" r="1.5" fill="white"/>
						<path d="M3 14l4-4 3 3 4-4 4 5" stroke="white" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
					选择图片
				</button>
			</view>
			
			<!-- Tips Card -->
			<view class="tips-card">
				<view class="tips-title">💡 上传须知</view>
				<view class="tip-item">• 请上传人行征信中心出具的完整报告</view>
				<view class="tip-item">• PDF格式自动识别，图片需清晰可辨</view>
				<view class="tip-item">• 所有数据加密传输，保护您的隐私安全</view>
			</view>
			
			<!-- Bottom Spacing -->
			<view class="bottom-spacing"></view>
		</scroll-view>
		
		<!-- Tab Bar -->
		<TabBar :current="2" @change="onTabChange"></TabBar>
	</view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TabBar from '@/components/TabBar/index.vue'
import { uploadCreditReport } from '@/api/credit'

const uploadHint = ref('点击或拖拽文件到此处')
const isUploading = ref(false)

const goBack = () => {
	uni.navigateBack()
}

const chooseImage = () => {
	if (isUploading.value) return
	
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['album'],
		success: (res) => {
			if (res.tempFilePaths.length > 0) {
				uploadFile(res.tempFilePaths[0])
			}
		}
	})
}

const takePhoto = () => {
	if (isUploading.value) return
	
	uni.chooseImage({
		count: 1,
		sizeType: ['compressed'],
		sourceType: ['camera'],
		success: (res) => {
			if (res.tempFilePaths.length > 0) {
				uploadFile(res.tempFilePaths[0])
			}
		}
	})
}

const uploadFile = async (filePath: string) => {
	isUploading.value = true
	uploadHint.value = '正在上传...'
	
	try {
		const result: any = await uploadCreditReport(filePath)
		if (result.task_id) {
			// 跳转到进度页，带上task_id
			uni.navigateTo({
				url: `/pages/progress/progress?taskId=${result.task_id}`
			})
		} else {
			uni.showToast({ title: '上传失败', icon: 'none' })
			uploadHint.value = '点击或拖拽文件到此处'
		}
	} catch (error: any) {
		console.error('上传失败:', error)
		uni.showToast({ title: error.message || '上传失败', icon: 'none' })
		uploadHint.value = '点击或拖拽文件到此处'
	} finally {
		isUploading.value = false
	}
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
}

/* Page Header */
.page-header {
	display: flex;
	align-items: center;
	height: 88rpx;
	gap: 24rpx;
	
	.back-arrow {
		font-size: 44rpx;
		font-weight: 600;
		color: #1E293B;
		font-family: 'IBM Plex Sans', sans-serif;
		line-height: 1;
	}
	
	.page-title {
		flex: 1;
		text-align: center;
		font-size: 36rpx;
		font-weight: 700;
		color: #1E293B;
	}
	
	.header-spacer {
		width: 48rpx;
	}
}

/* Upload Zone */
.upload-zone {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 440rpx;
	border: 2rpx dashed rgba(99, 102, 241, 0.3);
	border-radius: 40rpx;
	background: #F8FAFC;
	gap: 24rpx;
	margin-top: 8rpx;
	
	.upload-icon {
		width: 96rpx;
		height: 96rpx;
	}
	
	.upload-hint {
		font-size: 28rpx;
		color: #64748B;
	}
	
	.upload-sub {
		font-size: 22rpx;
		color: #94A3B8;
	}
}

/* Action Row */
.action-row {
	display: flex;
	gap: 24rpx;
	margin-top: 24rpx;
}

.action-btn {
	flex: 1;
	height: 100rpx;
	border-radius: 50rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 12rpx;
	font-size: 28rpx;
	font-weight: 600;
	border: none;
	
	svg {
		width: 40rpx;
		height: 40rpx;
	}
	
	&.outline {
		background: #FFFFFF;
		border: 2rpx solid #6366F1;
		color: #6366F1;
	}
	
	&.filled {
		background: #6366F1;
		color: #FFFFFF;
	}
}

/* Tips Card */
.tips-card {
	background: #EEF2FF;
	border-radius: 28rpx;
	padding: 32rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
	margin-top: 24rpx;
	
	.tips-title {
		font-size: 26rpx;
		font-weight: 600;
		color: #1E293B;
	}
	
	.tip-item {
		font-size: 22rpx;
		color: #64748B;
	}
}

/* Bottom Spacing */
.bottom-spacing {
	height: 140rpx;
}
</style>
