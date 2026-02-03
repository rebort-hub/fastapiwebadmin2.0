-- 为menu表添加permission字段（如果不存在）
-- 并将roles字段的数据迁移到permission字段

-- 1. 添加permission字段（如果不存在）
ALTER TABLE menu 
ADD COLUMN IF NOT EXISTS permission VARCHAR(100) 
COMMENT '权限标识 如: user:add';

-- 2. 将roles字段的数据迁移到permission字段
UPDATE menu 
SET permission = roles 
WHERE permission IS NULL 
AND roles IS NOT NULL 
AND roles != '' 
AND roles != '0';

-- 3. 为permission字段添加索引
CREATE INDEX IF NOT EXISTS idx_menu_permission ON menu(permission);

-- 4. 查看迁移结果
SELECT id, title, menu_type, roles, permission 
FROM menu 
WHERE menu_type = 3 
LIMIT 10;
