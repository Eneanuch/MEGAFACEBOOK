Имеется API<br>
Обратиться можно по следующим адресам<br>
<br>
<br>
Для получения всего:<br>
GET /api/v2/users<br>
выдает json со всеми пользовательскими данными<br>
<br>
GET /api/v2/posts<br>
выдает json со всеми постами<br>
<br>
<br>
Для получения обьекта: <br>
GET /api/v2/users/<int:user_id> - id пользователся, которого хотим получить<br>
выдает json пользователя<br>
<br>
GET /api/v2/posts/<int:post_id> - id поста, которого хотим получить<br>
выдает json поста<br>
<br>
<br>
Для добавления:<br>
<code>POST /api/v2/users<br>
json={<br>
        id=['id'], // id пользователя<br>
        name=['name'], // имя<br>
        surname=['surname'], // фамилия <br>
        photo=['photo'], // фото (ссылка на сервере)<br>
        email=['email'], // почта<br>
        phone=['phone'], // телефон <br>
        city=['city'], // город<br>
        hashed_password=['hashed_password'], // захешированный пароль<br>
        registration_date=datetime.strptime(дата в datetime,<br>
        '%y-%m-%d %H:%M:%S'), // дата регистрации <br>
        birthday=datetime.strptime(дата в datetime, '%y-%m-%d %H:%M:%S') // дата рождения<br>
}<br></code>
<br>
<code>POST /api/v2/posts<br>
json={<br>
    id=args['id'], // id поста <br>
    author=args['author'], // id автора<br>
    text=args['text'], // текст записи <br>
    photo=args['photo'], // фото (ссылка на сервере)<br>
    date=datetime.strptime(дата в datetime, '%y-%m-%d %H:%M:%S') // дата публикации <br>
}</code><br>
<br>
<br>
Для редактирования: <br>
<code>PUT /api/v2/users/<int:user_id> user_id - id пользователся, которого редактируем <br>
json={<br>
    id=['id'], // id пользователя<br>
    name=['name'], // имя<br>
    surname=['surname'], // фамилия <br>
    photo=['photo'], // фото (ссылка на сервере)<br>
    email=['email'], // почта<br>
    phone=['phone'], // телефон <br>
    city=['city'], // город<br>
    hashed_password=['hashed_password'], // захешированный пароль<br>
    registration_date=datetime.strptime(дата в datetime,<br>
    '%y-%m-%d %H:%M:%S'), // дата регистрации <br>
    birthday=datetime.strptime(дата в datetime, '%y-%m-%d %H:%M:%S') // дата рождения<br>
}<br></code>
<br>
PUT /api/v2/posts/<int:post_id> - id поста, которого хотим изменить <br>
json={<br>
id=args['id'], // id поста <br>
author=args['author'], // id автора<br>
text=args['text'], // текст записи <br>
photo=args['photo'], // фото (ссылка на сервере)<br>
date=datetime.strptime(дата в datetime, '%y-%m-%d %H:%M:%S') // дата публикации <br>
}</code><br>
<br>
<br>
Для удаления: 
DELETE /api/v2/users/<int:user_id> user_id - id пользователся, которого хотим удалить <br>
<br>
DELETE /api/v2/posts/<int:post_id> post_id - id поста, которого хотим удалить <br>
