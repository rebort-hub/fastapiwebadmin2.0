/**
 * 时间格式化工具
 */

/**
 * 格式化时间为 yyyy-mm-dd hh:mm:ss 格式
 * @param time 时间字符串或Date对象
 * @returns 格式化后的时间字符串，如果时间为空则返回 '-'
 */
export function formatDateTime(time: string | Date | null | undefined): string {
  if (!time) {
    return '-';
  }
  
  try {
    const date = typeof time === 'string' ? new Date(time) : time;
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '-';
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch (error) {
    console.error('时间格式化失败:', error);
    return '-';
  }
}

/**
 * 格式化时间为 yyyy-mm-dd 格式
 * @param time 时间字符串或Date对象
 * @returns 格式化后的日期字符串，如果时间为空则返回 '-'
 */
export function formatDate(time: string | Date | null | undefined, format?: string): string {
  if (!time) {
    return '-';
  }
  
  try {
    const date = typeof time === 'string' ? new Date(time) : time;
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
      return '-';
    }
    
    // 如果没有指定格式，默认返回 yyyy-mm-dd hh:mm:ss
    if (!format) {
      return formatDateTime(time);
    }
    
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    // 简单的格式替换
    return format
      .replace(/YYYY/g, String(year))
      .replace(/mm/g, month)
      .replace(/dd/g, day)
      .replace(/HH/g, hours)
      .replace(/MM/g, minutes)
      .replace(/SS/g, seconds);
  } catch (error) {
    console.error('日期格式化失败:', error);
    return '-';
  }
}

/**
 * 根据时间返回问候语
 * @param time 时间对象
 * @returns 问候语字符串
 */
export function formatAxis(time: Date): string {
  const hour = time.getHours();
  
  if (hour < 6) {
    return '凌晨好';
  } else if (hour < 9) {
    return '早上好';
  } else if (hour < 12) {
    return '上午好';
  } else if (hour < 14) {
    return '中午好';
  } else if (hour < 17) {
    return '下午好';
  } else if (hour < 19) {
    return '傍晚好';
  } else if (hour < 22) {
    return '晚上好';
  } else {
    return '夜里好';
  }
}