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
			<view class="page-title">上传征信报告</view>
			<view class="header-spacer"></view>
		</view>
		
		<!-- Content -->
		<scroll-view class="content" scroll-y>
			<!-- Upload Zone -->
			<view class="upload-zone" @click="chooseImage">
				<view class="upload-icon">
					<view class="icon-doc"></view>
				</view>
				<view class="upload-hint">点击或拖拽文件到此处</view>
				<view class="upload-sub">支持 JPG / PNG / PDF 格式，最大 20MB</view>
			</view>
			
			<!-- Action Buttons -->
			<view class="action-row">
				<button class="action-btn outline" @click="takePhoto">
					<view class="btn-camera-icon"></view>
					拍照
				</button>
				<button class="action-btn filled" @click="chooseImage">
					<view class="btn-gallery-icon"></view>
					相册
				</button>
			</view>
			
			<!-- Selected File Preview -->
			<view class="file-preview" v-if="selectedFile">
				<view class="file-info">
					<view class="file-name">{{ selectedFile.name }}</view>
					<view class="file-size">{{ formatFileSize(selectedFile.size) }}</view>
				</view>
				<view class="file-remove" @click="removeFile">×</view>
			</view>
			
			<!-- Tips Card -->
			<view class="tips-card">
				<view class="tips-title">上传须知</view>
				<view class="tip-item">1. 请上传完整的征信报告图片或PDF文件</view>
				<view class="tip-item">2. 确保图片清晰、光线充足、无反光</view>
				<view class="tip-item">3. 文件大小不要超过20MB</view>
				<view class="tip-item">4. 支持多人报告，但每次只处理一份</view>
			</view>
			
			<!-- Start Analysis Button -->
			<button 
				class="btn-primary" 
				:disabled="!selectedFile || uploading" 
				@click="startAnalysis"
			>
				<template v-if="uploading">
					<view class="loading-icon"></view>
					{{ uploadProgress }}%
				</template>
				<template v-else>
					开始分析
				</template>
			</button>
		</scroll-view>
	</view>
</template>

<script>
	import { uploadCreditReport } from '@/api/credit.js';

	export default {
		data() {
			return {
				selectedFile: null,
				uploading: false,
				uploadProgress: 0
			}
		},
		methods: {
			goBack() {
				uni.navigateBack();
			},
			chooseImage() {
				uni.chooseImage({
					count: 1,
					sizeType: ['compressed'],
					sourceType: ['album'],
					success: (res) => {
						if (res.tempFilePaths.length > 0) {
							this.selectedFile = {
								path: res.tempFilePaths[0],
								name: res.tempFiles[0].name || '未命名文件',
								size: res.tempFiles[0].size
							};
						}
					}
				});
			},
			takePhoto() {
				uni.chooseImage({
					count: 1,
					sizeType: ['compressed'],
					sourceType: ['camera'],
					success: (res) => {
						if (res.tempFilePaths.length > 0) {
							this.selectedFile = {
								path: res.tempFilePaths[0],
								name: 'camera_' + Date.now() + '.jpg',
								size: res.tempFiles[0].size
							};
						}
					}
				});
			},
			removeFile() {
				this.selectedFile = null;
			},
			formatFileSize(size) {
				if (size < 1024) return size + 'B';
				if (size < 1024 * 1024) return (size / 1024).toFixed(1) + 'KB';
				return (size / (1024 * 1024)).toFixed(1) + 'MB';
			},
			startAnalysis() {
				if (!this.selectedFile) return;
				
				this.uploading = true;
				this.uploadProgress = 0;
				
				// 上传文件到AI服务
				uploadCreditReport(this.selectedFile.path, (progress) => {
					this.uploadProgress = progress;
				}).then((res) => {
					if (res.task_id) {
						// 上传成功，跳转到进度页
						uni.navigateTo({
							url: '/pages/credit/progress?taskId=' + res.task_id
						});
					} else {
						uni.showToast({ title: '上传失败', icon: 'none' });
						this.uploading = false;
					}
				}).catch((err) => {
					console.error('上传失败:', err);
					uni.showToast({ title: '上传失败: ' + (err.message || '未知错误'), icon: 'none' });
					this.uploading = false;
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
	gap: 24rpx;
	overflow-y: auto;
}

/* Upload Zone */
.upload-zone {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 440rpx;
	border: 4rpx dashed rgba(99,102,241,0.3);
	border-radius: 40rpx;
	background: #F8FAFC;
	gap: 24rpx;
}

.upload-icon {
	width: 96rpx;
	height: 96rpx;
	border-radius: 20rpx;
	background: #EEF2FF;
	display: flex;
	align-items: center;
	justify-content: center;
}

.icon-doc {
	width: 48rpx;
	height: 48rpx;
	border: 4rpx solid #6366F1;
	border-radius: 6rpx;
	position: relative;
	
	&::before {
		content: '';
		position: absolute;
		top: 8rpx;
		left: 8rpx;
		right: 8rpx;
		height: 4rpx;
		background: #6366F1;
	}
	
	&::after {
		content: '';
		position: absolute;
		top: 16rpx;
		left: 8rpx;
		right: 8rpx;
		height: 4rpx;
		background: #6366F1;
	}
}

.upload-hint {
	font-size: 28rpx;
	color: #64748B;
}

.upload-sub {
	font-size: 22rpx;
	color: #94A3B8;
}

/* Action Buttons */
.action-row {
	display: flex;
	gap: 24rpx;
}

.action-btn {
	flex: 1;
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100rpx;
	border-radius: 50rpx;
	gap: 12rpx;
	font-size: 28rpx;
	font-weight: 600;
	border: none;
	
	&.outline {
		background: #FFFFFF;
		border: 3rpx solid #6366F1;
		color: #6366F1;
	}
	
	&.filled {
		background: #6366F1;
		color: #FFFFFF;
	}
}

.btn-camera-icon {
	width: 40rpx;
	height: 40rpx;
	border: 3rpx solid #6366F1;
	border-radius: 8rpx;
	position: relative;
	
	&::after {
		content: '';
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 20rpx;
		height: 20rpx;
		border-radius: 50%;
		background: #6366F1;
	}
}

.btn-gallery-icon {
	width: 40rpx;
	height: 40rpx;
	border: 3rpx solid #FFFFFF;
	border-radius: 8rpx;
	position: relative;
	
	&::before {
		content: '';
		position: absolute;
		top: 8rpx;
		left: 8rpx;
		width: 24rpx;
		height: 20rpx;
		background: #FFFFFF;
		border-radius: 2rpx;
	}
}

/* File Preview */
.file-preview {
	display: flex;
	align-items: center;
	background: #FFFFFF;
	border-radius: 24rpx;
	padding: 24rpx;
	gap: 16rpx;
	box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}

.file-info {
	flex: 1;
	display: flex;
	flex-direction: column;
	gap: 4rpx;
}

.file-name {
	font-size: 28rpx;
	font-weight: 600;
	color: #1E293B;
}

.file-size {
	font-size: 22rpx;
	color: #94A3B8;
}

.file-remove {
	width: 48rpx;
	height: 48rpx;
	border-radius: 50%;
	background: #FEF2F2;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	font-weight: 600;
	color: #EF4444;
}

/* Tips Card */
.tips-card {
	background: #EEF2FF;
	border-radius: 28rpx;
	padding: 32rpx;
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.tips-title {
	font-size: 26rpx;
	font-weight: 600;
	color: #1E293B;
}

.tip-item {
	font-size: 22rpx;
	color: #64748B;
	line-height: 1.5;
}

/* Primary Button */
.btn-primary {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 100rpx;
	background: linear-gradient(90deg, #6366F1, #A855F7);
	border-radius: 50rpx;
	color: #FFFFFF;
	font-size: 30rpx;
	font-weight: 700;
	border: none;
	box-shadow: 0 8rpx 32rpx rgba(99,102,241,0.3);
	
	&[disabled] {
		background: #CBD5E1;
		box-shadow: none;
	}
}

.loading-icon {
	width: 40rpx;
	height: 40rpx;
	border: 4rpx solid rgba(255,255,255,0.3);
	border-top-color: #FFFFFF;
	border-radius: 50%;
	animation: spin 1s linear infinite;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}
</style>
