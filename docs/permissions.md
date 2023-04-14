Как думаешь как реализвовать систему прав. 

User -> Permissions 
     -> Groups -> Permissions 

Админка -> ???

Модель пермс будет иметь поле code 
которая будет содержать все доступы к другим моделям 
Формат кодов будет таков: 
     code -> "{permission_code}_{model_name}"
Если у юзера есть админ права то его права пользвателя т.е. "edit_user delete_user read_user create_user"
тогда он может изменять записи других пользователей.

##### Где происходит аутентификация? 

В роуте через dependency - CheckPermission("{permission_code}")
