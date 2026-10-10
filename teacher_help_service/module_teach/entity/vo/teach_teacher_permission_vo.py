from typing import List
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SaveTeacherPermissionModel(BaseModel):
    """
    保存角色业务权限
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    role_id: int = Field(description='角色ID')
    menu_ids: List[int] = Field(default_factory=list, max_length=1000, description='勾选的业务菜单/按钮ID')
