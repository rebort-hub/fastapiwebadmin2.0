"""
公共依赖项
"""

from fastapi import Header, HTTPException, status


async def get_current_user_id(
    authorization: str = Header(..., description="Bearer token")
) -> int:
    """从token中获取当前用户ID"""
    from app.api.v1.system.auth.service import AuthService
    
    # 提取token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证方式"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # 验证token
    payload = AuthService.verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效"
        )
    
    return int(user_id)