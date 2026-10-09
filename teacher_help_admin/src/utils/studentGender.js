/**
 * 学员性别口径（teach_students.gender）：0未知 1男 2女
 *
 * 注意：与若依用户字典 sys_user_sex（0男 1女 2未知）取值含义不同，
 * 学员相关页面禁止使用 sys_user_sex 展示/录入学员性别，统一使用本文件。
 */
export const STUDENT_GENDER_OPTIONS = [
  { label: '未知', value: '0', elTagType: 'default' },
  { label: '男', value: '1', elTagType: 'default' },
  { label: '女', value: '2', elTagType: 'default' }
];

export function studentGenderLabel(value) {
  const option = STUDENT_GENDER_OPTIONS.find(item => item.value === String(value ?? ''));
  return option ? option.label : '未知';
}
