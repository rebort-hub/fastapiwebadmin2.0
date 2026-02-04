# 强制下线弹窗调试指南

## 问题描述

用户被强制下线后，应该看到弹窗提示"您已被强制下线，请重新登录"，并有"重新登录"按钮。但实际上用户看不到弹窗或按钮。

## 可能的原因

### 1. 弹窗被遮挡
- Element Plus 弹窗的 z-index 可能太低
- 页面上有其他元素遮挡了弹窗

### 2. 弹窗没有正确触发
- 401 错误没有被正确捕获
- 错误消息格式不匹配

### 3. 多次触发导致冲突
- 多个请求同时失败，触发多个弹窗
- 弹窗状态管理有问题

## 调试步骤

### 步骤 1: 测试弹窗组件

1. 打开测试页面：`frontend/test-force-offline.html`
2. 在浏览器中打开这个文件
3. 点击"测试强制下线弹窗"按钮
4. 检查是否能看到弹窗

**预期结果**：
- 应该看到一个居中的警告弹窗
- 标题："系统提示"
- 内容："您已被强制下线，请重新登录"
- 按钮："重新登录"

**如果看不到弹窗**：
- 说明 Element Plus 组件有问题
- 检查浏览器控制台是否有错误
- 检查 Element Plus 版本是否兼容

### 步骤 2: 检查网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 在 B 窗口中点击任何菜单
4. 查看失败的请求

**检查项**：
- 请求是否返回 401 状态码
- 响应体中是否包含 "强制下线" 字样
- 响应格式是否正确

**示例响应**：
```json
{
  "detail": "您已被强制下线，请重新登录"
}
```

### 步骤 3: 检查控制台日志

在浏览器控制台中查看是否有以下日志：

**正常情况**：
```
[拦截器] 捕获 401 错误
[拦截器] 错误消息: 您已被强制下线，请重新登录
[拦截器] 显示强制下线弹窗
```

**异常情况**：
- 如果没有任何日志，说明拦截器没有被触发
- 如果有错误日志，说明拦截器执行出错

### 步骤 4: 添加调试日志

在 `frontend/src/utils/request.ts` 中添加调试日志：

```typescript
// 处理 401 未授权错误（包括强制下线）
if (error.response.status === 401) {
    console.log('[拦截器] 捕获 401 错误');
    console.log('[拦截器] 错误消息:', errorMessage);
    
    // 检查是否是强制下线
    if (errorMessage && errorMessage.includes('强制下线')) {
        console.log('[拦截器] 检测到强制下线');
        console.log('[拦截器] isShowingForceOfflineDialog:', isShowingForceOfflineDialog);
        
        // 防止重复弹窗
        if (isShowingForceOfflineDialog) {
            console.log('[拦截器] 已有弹窗显示，跳过');
            return Promise.reject(error);
        }
        isShowingForceOfflineDialog = true;
        console.log('[拦截器] 准备显示弹窗');
        
        // 使用 Promise 方式确保弹窗正确显示
        ElMessageBox.alert(errorMessage, '系统提示', {
            confirmButtonText: '重新登录',
            type: 'warning',
            showClose: false,
            closeOnClickModal: false,
            closeOnPressEscape: false,
            center: true
        }).then(() => {
            console.log('[拦截器] 用户点击了重新登录');
            Session.clear();
            window.location.href = handlerRedirectUrl() || '/';
        }).catch(() => {
            console.log('[拦截器] 弹窗被关闭');
            Session.clear();
            window.location.href = handlerRedirectUrl() || '/';
        });
    }
}
```

### 步骤 5: 检查 Element Plus 样式

检查页面中是否正确加载了 Element Plus 的 CSS：

```html
<!-- 在 index.html 中应该有 -->
<link rel="stylesheet" href="...element-plus.css">
```

或者在 main.ts 中：

```typescript
import 'element-plus/dist/index.css'
```

### 步骤 6: 检查弹窗 z-index

在浏览器开发者工具中：

1. 点击"Elements"标签
2. 查找 `.el-message-box__wrapper` 元素
3. 检查其 z-index 值

**正常情况**：
- z-index 应该是一个很大的数字（如 2000+）
- 应该在页面最上层

**如果 z-index 太小**：
- 在全局 CSS 中添加：
```css
.el-message-box__wrapper {
    z-index: 9999 !important;
}
```

## 解决方案

### 方案 1: 使用原生 confirm（临时方案）

如果 Element Plus 弹窗有问题，可以临时使用原生弹窗：

```typescript
if (errorMessage && errorMessage.includes('强制下线')) {
    // 使用原生弹窗
    const confirmed = window.confirm(errorMessage + '\n\n点击"确定"重新登录');
    Session.clear();
    window.location.href = handlerRedirectUrl() || '/';
    return Promise.reject(error);
}
```

### 方案 2: 直接跳转（最简单）

如果不需要弹窗，直接跳转：

```typescript
if (errorMessage && errorMessage.includes('强制下线')) {
    // 显示简单提示
    alert('您已被强制下线，即将跳转到登录页');
    Session.clear();
    window.location.href = handlerRedirectUrl() || '/';
    return Promise.reject(error);
}
```

### 方案 3: 使用 ElMessage（轻量级）

使用顶部通知代替弹窗：

```typescript
if (errorMessage && errorMessage.includes('强制下线')) {
    ElMessage({
        message: '您已被强制下线，3秒后跳转到登录页',
        type: 'warning',
        duration: 3000,
        onClose: () => {
            Session.clear();
            window.location.href = handlerRedirectUrl() || '/';
        }
    });
    
    // 3秒后自动跳转
    setTimeout(() => {
        Session.clear();
        window.location.href = handlerRedirectUrl() || '/';
    }, 3000);
    
    return Promise.reject(error);
}
```

## 推荐的最终方案

结合多种方式，确保用户一定能看到提示：

```typescript
if (errorMessage && errorMessage.includes('强制下线')) {
    // 防止重复弹窗
    if (isShowingForceOfflineDialog) {
        return Promise.reject(error);
    }
    isShowingForceOfflineDialog = true;
    
    // 1. 先显示顶部消息
    ElMessage({
        message: errorMessage,
        type: 'warning',
        duration: 0, // 不自动关闭
        showClose: true
    });
    
    // 2. 然后显示弹窗
    ElMessageBox.alert(errorMessage, '系统提示', {
        confirmButtonText: '重新登录',
        type: 'warning',
        showClose: false,
        closeOnClickModal: false,
        closeOnPressEscape: false,
        center: true,
        customClass: 'force-offline-dialog' // 自定义样式类
    }).then(() => {
        Session.clear();
        window.location.href = handlerRedirectUrl() || '/';
    }).catch(() => {
        Session.clear();
        window.location.href = handlerRedirectUrl() || '/';
    });
    
    return Promise.reject(error);
}
```

然后在全局 CSS 中添加：

```css
/* 确保强制下线弹窗在最上层 */
.force-offline-dialog {
    z-index: 9999 !important;
}

.force-offline-dialog .el-message-box {
    z-index: 9999 !important;
}
```

## 测试清单

- [ ] 测试页面中的弹窗能正常显示
- [ ] 浏览器控制台没有错误
- [ ] Network 标签中能看到 401 响应
- [ ] 响应体包含"强制下线"字样
- [ ] 控制台有拦截器的调试日志
- [ ] Element Plus CSS 正确加载
- [ ] 弹窗 z-index 足够大
- [ ] 用户能看到弹窗
- [ ] 用户能点击"重新登录"按钮
- [ ] 点击后能跳转到登录页

## 常见问题

### Q1: 为什么看不到弹窗？

**A**: 可能的原因：
1. Element Plus 没有正确安装或导入
2. CSS 没有加载
3. 弹窗被其他元素遮挡
4. 拦截器没有被触发

**解决方法**：
- 检查 package.json 中是否有 element-plus
- 检查 main.ts 中是否导入了 CSS
- 使用浏览器开发者工具检查元素
- 添加调试日志

### Q2: 弹窗一闪而过？

**A**: 可能是多个请求同时失败，触发了多个弹窗。

**解决方法**：
- 使用 `isShowingForceOfflineDialog` 标志防止重复
- 确保标志在正确的时机重置

### Q3: 点击按钮没反应？

**A**: 可能是事件处理有问题。

**解决方法**：
- 检查 `.then()` 和 `.catch()` 是否正确
- 添加 console.log 确认事件被触发
- 检查 Session.clear() 和 window.location.href 是否正常

### Q4: 跳转到错误的页面？

**A**: `handlerRedirectUrl()` 返回了错误的 URL。

**解决方法**：
- 直接使用 `window.location.href = '/login'`
- 或者 `window.location.href = '/'`

## 总结

如果按照以上步骤调试后仍然有问题，建议：

1. 使用原生 `alert()` 或 `confirm()` 作为临时方案
2. 检查 Element Plus 版本兼容性
3. 查看 Element Plus 官方文档的 MessageBox 示例
4. 在项目的 GitHub Issues 中搜索类似问题

最重要的是确保用户被强制下线后能够：
1. 看到明确的提示信息
2. 能够重新登录
3. 不会卡在当前页面
